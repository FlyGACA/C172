// Phase 8 viewer core: renderer, sky, light, apron, post-processing and model loading.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { createSky, apronTextures, standMarkings, HAZE } from './sky.js';

// What each quality level draws. ao: ambient occlusion (contact shading); bloom: the glow of lights and of the sun
// on glossy paint; grade: a little contrast and a vignette; glass: 'clear' lets the picture behind show through
// with true reflections, 'tint' is the cheap kind.
export const QUALITY = {
  high: { file: 'models/C172N_realistic_high.glb', pixelRatio: 2, shadow: 4096, ao: true, bloom: true, grade: true, glass: 'clear', anisotropy: 16, apron: 2048 },
  medium: { file: 'models/C172N_realistic_medium.glb', pixelRatio: 2, shadow: 2048, ao: false, bloom: true, grade: true, glass: 'tint', anisotropy: 8, apron: 2048 },
  low: { file: 'models/C172N_realistic_low.glb', pixelRatio: 1.5, shadow: 1024, ao: false, bloom: false, grade: false, glass: 'tint', anisotropy: 4, apron: 1024 },
};

export function pickQuality(qs) {
  const q = qs.get('q');
  if (q && QUALITY[q]) return q;
  const mem = navigator.deviceMemory || 8;
  const mobile = /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent) || innerWidth < 800;
  // a tablet has the screen and the memory for the medium level; a telephone gets the low one
  const tablet = mobile && Math.min(screen.width, screen.height) >= 700;
  if (mem <= 2 || (mobile && !tablet)) return 'low';
  if (tablet || mem <= 4 || (navigator.hardwareConcurrency || 8) <= 4) return 'medium';
  return 'high';
}

// The last pass, on the finished picture: a gentle S-curve, a little more colour, darker corners.
const GradeShader = {
  uniforms: { tDiffuse: { value: null }, contrast: { value: 0.10 }, saturation: { value: 1.10 }, vignette: { value: 0.22 } },
  vertexShader: /* glsl */`varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: /* glsl */`
    uniform sampler2D tDiffuse; uniform float contrast; uniform float saturation; uniform float vignette; varying vec2 vUv;
    void main() {
      vec4 c = texture2D(tDiffuse, vUv);
      vec3 s = c.rgb * c.rgb * (3.0 - 2.0 * c.rgb);                 // smoothstep: darker darks, brighter lights
      vec3 col = mix(c.rgb, s, contrast);
      float l = dot(col, vec3(0.2126, 0.7152, 0.0722));
      col = mix(vec3(l), col, saturation);
      vec2 d = vUv - 0.5;
      col *= 1.0 - vignette * smoothstep(0.25, 0.95, dot(d, d) * 2.0);
      gl_FragColor = vec4(col, c.a);
    }`,
};

export class Viewer {
  constructor(container, quality, opts = {}) {
    this.container = container;
    this.qualityName = quality;
    // a software renderer (the tests) cannot afford the passes, a large shadow map or anisotropic filtering:
    // fx=1 in the address gives them to it all the same, for a still picture
    this.fx = opts.fx ?? !opts.test;
    this.q = this.fx ? QUALITY[quality] : { ...QUALITY[quality], shadow: Math.min(1024, QUALITY[quality].shadow), anisotropy: 1, apron: 1024 };
    this.usePasses = this.fx && (this.q.ao || this.q.bloom || this.q.grade);
    this.renderer = new THREE.WebGLRenderer({ antialias: !this.usePasses, alpha: false, powerPreference: 'high-performance', preserveDrawingBuffer: !!opts.test });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, this.q.pixelRatio));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.prepend(this.renderer.domElement);
    this.labels = new CSS2DRenderer();
    this.labels.domElement.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:2';
    container.append(this.labels.domElement);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(HAZE);
    this.scene.fog = new THREE.Fog(HAZE, 70, 520);          // the apron fades into the haze of the horizon
    this.camera = new THREE.PerspectiveCamera(42, 1, 0.03, 900);
    this.camera.position.set(-9, 3.2, 9);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true; this.controls.dampingFactor = 0.08;
    this.controls.maxPolarAngle = Math.PI * 0.49; this.controls.minDistance = 0.05; this.controls.maxDistance = 60;
    this.controls.target.set(0, 1.0, 0);

    // the sun: mid-morning, a little ahead of the left wing (elevation 42°, azimuth 35°, as in the reference renders)
    const el = THREE.MathUtils.degToRad(42), az = THREE.MathUtils.degToRad(35);
    this.sunDir = new THREE.Vector3(Math.cos(el) * Math.sin(az), Math.sin(el), Math.cos(el) * Math.cos(az));
    this.sun = new THREE.DirectionalLight(0xfff0d8, 4.0);
    this.sun.position.copy(this.sunDir).multiplyScalar(30);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(this.q.shadow, this.q.shadow);
    const sc = this.sun.shadow.camera; sc.left = -8; sc.right = 8; sc.top = 8; sc.bottom = -8; sc.near = 5; sc.far = 70;
    this.sun.shadow.bias = -0.0004; this.sun.shadow.normalBias = 0.02; this.sun.shadow.radius = 2.5;
    this.scene.add(this.sun, this.sun.target);
    this.scene.add(new THREE.HemisphereLight(0xcfe2ff, 0x8c8477, 0.45));      // the sky from above, the apron from below

    this.sky = createSky(this.sunDir);
    this.scene.add(this.sky);

    this.composer = null;
    this.aoEnabled = this.q.ao && this.fx;
    this.renderer.info.autoReset = false;   // keep per-frame totals across composer passes
    this.clock = new THREE.Clock();
    this.onFrame = [];
    this._resize = () => this.resize();
    new ResizeObserver(this._resize).observe(container);
    this.resize();
    if (this.usePasses) this._buildPasses();
  }

  /** The light of the sky on the model: what the paint and the glass reflect. Made from the sky dome itself. */
  async loadEnvironment() {
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    const box = new THREE.Scene();
    const dome = createSky(this.sunDir);
    dome.scale.setScalar(50);
    box.add(dome);
    this.scene.environment = pmrem.fromScene(box, 0, 0.1, 100).texture;
    this.scene.environmentIntensity = 1.0;
    dome.material.dispose(); dome.geometry.dispose(); pmrem.dispose();
  }

  addGround() {
    const t = apronTextures(this.q.apron, 4);
    const tile = 20;                                          // metres a tile: four slabs of five metres each way
    for (const k of ['map', 'roughnessMap', 'normalMap']) { t[k].repeat.set(1200 / tile, 1200 / tile); t[k].anisotropy = this.q.anisotropy; }
    const mat = new THREE.MeshStandardMaterial({ ...t, roughness: 1, metalness: 0, normalScale: new THREE.Vector2(0.9, 0.9) });
    // large patches of lighter and darker concrete, so that the tiles do not show as a pattern
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d'); g.fillStyle = '#808080'; g.fillRect(0, 0, 256, 256);
    let seed = 99; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
    for (let k = 0; k < 220; k++) { const x = rnd() * 256, y = rnd() * 256, r = 6 + rnd() * 34, v = rnd() > 0.5 ? 255 : 0; const grad = g.createRadialGradient(x, y, 0, x, y, r); grad.addColorStop(0, `rgba(${v},${v},${v},0.16)`); grad.addColorStop(1, `rgba(${v},${v},${v},0)`); g.fillStyle = grad; g.fillRect(x - r, y - r, 2 * r, 2 * r); }
    const macro = new THREE.CanvasTexture(c); macro.wrapS = macro.wrapT = THREE.RepeatWrapping;
    mat.onBeforeCompile = (shader) => {
      shader.uniforms.macroMap = { value: macro };
      shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vMacro;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvMacro = (modelMatrix * vec4(transformed, 1.0)).xz / 180.0;');
      shader.fragmentShader = shader.fragmentShader.replace('#include <common>', '#include <common>\nuniform sampler2D macroMap; varying vec2 vMacro;').replace('#include <map_fragment>', '#include <map_fragment>\ndiffuseColor.rgb *= 0.74 + 0.52 * texture2D(macroMap, vMacro).r;');
    };
    const slab = new THREE.Mesh(new THREE.CircleGeometry(600, 96), mat);
    slab.rotation.x = -Math.PI / 2; slab.receiveShadow = true; slab.raycast = () => {};
    this.stand = standMarkings();
    this.ground = new THREE.Group(); this.ground.name = '_ground';      // the apron and what is painted on it
    this.ground.add(slab, this.stand);
    this.scene.add(this.ground);
  }

  /** Put the stop bar of the parking stand at a Z (the nose wheel's). */
  placeStand(z) { if (this.stand) this.stand.position.z = z - this.stand.userData.barAhead; }

  async loadModel(url, onProgress) {
    const draco = new DRACOLoader();
    draco.setDecoderPath('vendor/three/examples/jsm/libs/draco/gltf/');
    const loader = new GLTFLoader().setDRACOLoader(draco);
    const gltf = await new Promise((res, rej) => loader.load(url, res, (e) => onProgress && onProgress(e.total ? e.loaded / e.total : 0.5), rej));
    this.scene.add(gltf.scene);
    this.model = gltf.scene;
    this.tuneMaterials(gltf.scene);
    return gltf.scene;
  }

  /** Give the materials of the model what the file format does not carry: the clear coat of the paint, glass that reflects. */
  tuneMaterials(root) {
    const made = new Map();
    const physical = (m) => {
      if (m.isMeshPhysicalMaterial) return m;
      if (!made.has(m)) { const p = new THREE.MeshPhysicalMaterial(); THREE.MeshStandardMaterial.prototype.copy.call(p, m); p.name = m.name; made.set(m, p); }
      return made.get(m);
    };
    const seen = new Set(), clear = this.q.glass === 'clear' && this.fx;
    this.glass = [];                       // the window and instrument glass, with how strongly each mirrors the sky from outside
    // Bright metal in the cabin would mirror the open sky, which it cannot see: under the roof it gets a third of it.
    const indoors = new Map();
    const inCabin = (o) => /^(INTERIOR|PANEL)$/.test(o.userData.system ?? o.parent?.userData.system ?? '');
    root.traverse((o) => {
      if (!o.isMesh || !o.material || Array.isArray(o.material)) return;
      if (inCabin(o) && o.material.metalness > 0.5) {
        if (!indoors.has(o.material)) { const m = o.material.clone(); m.name = o.material.name; m.envMapIntensity = 0.3; indoors.set(o.material, m); }
        o.material = indoors.get(o.material);
      }
      const name = o.material.name || '';
      if (/^(skin_|paint_)/.test(name)) o.material = physical(o.material);
      if (/^glass_|^instrument_glass/.test(name) && clear) o.material = physical(o.material);
      const m = o.material;
      if (seen.has(m)) return;
      seen.add(m);
      for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap']) if (m[k]) m[k].anisotropy = this.q.anisotropy;
      if (/^(skin_|paint_)/.test(name)) { m.clearcoat = 1.0; m.clearcoatRoughness = 0.07; m.envMapIntensity = 1.0; }      // polyurethane over the colour
      else if (/^glass_/.test(name)) {
        if (clear) {                         // clear acrylic: what is behind shows through it, the sky shows on it
          m.transparent = false; m.opacity = 1; m.transmission = 1; m.thickness = 0.004; m.ior = 1.49; m.roughness = 0.03; m.metalness = 0;
          m.color.setRGB(0.93, 0.97, 0.96); m.attenuationColor = new THREE.Color(0.80, 0.93, 0.90); m.attenuationDistance = 0.05; m.envMapIntensity = 1.0; m.depthWrite = true;
        } else {                             // tinted film: thin, with the sky's reflection kept at its natural strength
          m.opacity = 0.14; m.color.setRGB(0.50, 0.62, 0.66); m.roughness = 0.03; m.metalness = 0; m.envMapIntensity = 5.0;
        }
      } else if (/^instrument_glass/.test(name)) {
        if (clear) { m.transparent = false; m.opacity = 1; m.transmission = 1; m.thickness = 0.002; m.ior = 1.5; m.roughness = 0.02; m.color.setRGB(1, 1, 1); m.envMapIntensity = 0.6; m.depthWrite = true; }
        else { m.opacity = 0.08; m.roughness = 0.02; m.envMapIntensity = 3.0; }
      }
      if (/^glass_|^instrument_glass/.test(name)) this.glass.push({ material: m, outdoors: m.envMapIntensity });
      // markings and lettering lie a millimetre over the surface they are on: from far away the depth buffer cannot
      // tell the two apart, so they are drawn as lying on top
      if (/^(markings|panel_placards)/.test(name)) { m.polygonOffset = true; m.polygonOffsetFactor = -2; m.polygonOffsetUnits = -6; }
    });
  }

  /**
   * From a seat in the cabin the inner face of the glass mirrors the cabin, which is dark, not the sky: seen from
   * there the windows are clear. Outside they carry the sky's reflection again.
   */
  setIndoors(on) {
    this.indoors = !!on;
    for (const g of this.glass || []) g.material.envMapIntensity = g.outdoors * (on ? 0.1 : 1);
  }

  _buildPasses() {
    const size = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    const rt = new THREE.WebGLRenderTarget(size.x, size.y, { type: THREE.HalfFloatType, samples: 4 });
    this.composer = new EffectComposer(this.renderer, rt);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    if (this.q.ao) {
      this.gtao = new GTAOPass(this.scene, this.camera, size.x, size.y);
      this.gtao.output = GTAOPass.OUTPUT.Default;
      this.gtao.updateGtaoMaterial({ radius: 0.35, distanceExponent: 1, thickness: 1, scale: 1.25, samples: 12, distanceFallOff: 1, screenSpaceRadius: false });
      this.gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, radiusExponent: 1, rings: 2, samples: 12 });
      this.gtao.enabled = this.aoEnabled;
      this.composer.addPass(this.gtao);
    }
    if (this.q.bloom) {
      // only what is much brighter than sunlit white paint glows: lamps, the sun on the clear coat, the sun itself
      this.bloom = new UnrealBloomPass(new THREE.Vector2(size.x, size.y), 0.28, 0.6, 2.6);
      this.composer.addPass(this.bloom);
    }
    this.composer.addPass(new OutputPass());
    if (this.q.grade) this.composer.addPass(new ShaderPass(GradeShader));
  }

  setAO(on) {
    this.aoEnabled = on && this.q.ao && this.fx;
    if (this.gtao) this.gtao.enabled = this.aoEnabled;
  }

  resize() {
    const w = this.container.clientWidth, h = this.container.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.labels.setSize(w, h);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
    if (this.composer) this.composer.setSize(w, h);
  }

  start() {
    const loop = () => {
      // dt moves what is drawn (cameras, doors): no more than a tenth of a second, so a slow frame is not a jump.
      // elapsed is for what must keep time with the clock (the simulation): up to half a second of it a frame,
      // so that a slow device does not see the aircraft's systems in slow motion.
      const raw = this.clock.getDelta();
      const dt = Math.min(0.1, raw), elapsed = Math.min(0.5, raw);
      for (const f of this.onFrame) f(dt, elapsed);
      if (!this.manualCamera) this.controls.update();      // the pilot's seat places the camera itself
      // the sky is always round the camera, and as far as the camera sees
      this.sky.position.copy(this.camera.position); this.sky.scale.setScalar(this.camera.far * 0.9);
      this.sky.material.uniforms.time.value += dt;
      this.renderer.info.reset();
      if (this.composer) this.composer.render(); else this.renderer.render(this.scene, this.camera);
      this.labels.render(this.scene, this.camera);
      this.raf = requestAnimationFrame(loop);
    };
    loop();
  }

  flyTo(pos, target, instant = false) {
    const to = { pos: new THREE.Vector3(...pos), tgt: new THREE.Vector3(...target) };
    if (instant) { this.camera.position.copy(to.pos); this.controls.target.copy(to.tgt); this.controls.update(); return; }
    this.camAnim = { t: 0, from: { pos: this.camera.position.clone(), tgt: this.controls.target.clone() }, to };
  }

  tickCamera(dt) {
    if (!this.camAnim) return;
    const a = this.camAnim; a.t = Math.min(1, a.t + dt / 0.9);
    const k = 1 - Math.pow(1 - a.t, 3);
    this.camera.position.lerpVectors(a.from.pos, a.to.pos, k);
    this.controls.target.lerpVectors(a.from.tgt, a.to.tgt, k);
    if (a.t >= 1) this.camAnim = null;
  }

  stats() {
    const i = this.renderer.info;
    return { calls: i.render.calls, triangles: i.render.triangles, textures: i.memory.textures, geometries: i.memory.geometries };
  }
}
