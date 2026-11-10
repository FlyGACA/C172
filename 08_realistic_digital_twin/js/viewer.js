// Phase 8 viewer core: renderer, environment, lighting, ground, post-processing and model loading.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export const QUALITY = {
  high: { file: 'models/C172N_realistic_high.glb', pixelRatio: 2, shadow: 2048, ao: true },
  medium: { file: 'models/C172N_realistic_medium.glb', pixelRatio: 1.5, shadow: 1024, ao: false },
  low: { file: 'models/C172N_realistic_low.glb', pixelRatio: 1, shadow: 512, ao: false },
};

export function pickQuality(qs) {
  const q = qs.get('q');
  if (q && QUALITY[q]) return q;
  const mem = navigator.deviceMemory || 8;
  const mobile = /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent) || innerWidth < 800;
  if (mobile || mem <= 2) return 'low';
  if (mem <= 4 || (navigator.hardwareConcurrency || 8) <= 4) return 'medium';
  return 'high';
}

export class Viewer {
  constructor(container, quality, opts = {}) {
    this.container = container;
    this.qualityName = quality;
    this.q = QUALITY[quality];
    this.renderer = new THREE.WebGLRenderer({ antialias: !this.q.ao, alpha: false, powerPreference: 'high-performance', preserveDrawingBuffer: !!opts.test });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, this.q.pixelRatio));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.95;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.prepend(this.renderer.domElement);
    this.labels = new CSS2DRenderer();
    this.labels.domElement.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:2';
    container.append(this.labels.domElement);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(42, 1, 0.03, 300);
    this.camera.position.set(-9, 3.2, 9);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true; this.controls.dampingFactor = 0.08;
    this.controls.maxPolarAngle = Math.PI * 0.49; this.controls.minDistance = 0.05; this.controls.maxDistance = 60;
    this.controls.target.set(0, 1.0, 0);

    // sun matching the generated sky (elevation 42°, azimuth 35°)
    const el = THREE.MathUtils.degToRad(42), az = THREE.MathUtils.degToRad(35);
    this.sun = new THREE.DirectionalLight(0xfff2e0, 3.2);
    this.sun.position.set(Math.cos(el) * Math.sin(az) * 30, Math.sin(el) * 30, Math.cos(el) * Math.cos(az) * 30);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(this.q.shadow, this.q.shadow);
    const sc = this.sun.shadow.camera; sc.left = -8; sc.right = 8; sc.top = 8; sc.bottom = -8; sc.near = 5; sc.far = 70;
    this.sun.shadow.bias = -0.0005; this.sun.shadow.normalBias = 0.02; this.sun.shadow.radius = 2;
    this.scene.add(this.sun, this.sun.target);
    this.scene.add(new THREE.HemisphereLight(0xcfe4ff, 0x6b6560, 0.35));

    this.composer = null;
    this.aoEnabled = this.q.ao;
    this.renderer.info.autoReset = false;   // keep per-frame totals across composer passes
    this.clock = new THREE.Clock();
    this.onFrame = [];
    this._resize = () => this.resize();
    new ResizeObserver(this._resize).observe(container);
    this.resize();
  }

  async loadEnvironment(url) {
    const tex = await new RGBELoader().loadAsync(url);
    tex.mapping = THREE.EquirectangularReflectionMapping;
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromEquirectangular(tex).texture;
    this.scene.environmentIntensity = 1.0;
    this.scene.background = tex;
    this.scene.backgroundBlurriness = 0.35;
    this.scene.backgroundIntensity = 0.85;
    pmrem.dispose();
  }

  addGround(texDir) {
    const tl = new THREE.TextureLoader();
    const rep = (t, cs) => { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(28, 28); t.anisotropy = 8; if (cs) t.colorSpace = THREE.SRGBColorSpace; return t; };
    const mat = new THREE.MeshStandardMaterial({ map: rep(tl.load(`${texDir}/apron_albedo.jpg`), true), normalMap: rep(tl.load(`${texDir}/apron_normal.png`)), roughness: 0.95, metalness: 0 });
    const g = new THREE.Mesh(new THREE.CircleGeometry(60, 72), mat);
    g.rotation.x = -Math.PI / 2; g.receiveShadow = true; g.name = '_ground';
    this.scene.add(g);
    // soft darkening under the aircraft so the horizon blends with the sky's ground band
    const fade = new THREE.Mesh(new THREE.CircleGeometry(60, 72), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.0 }));
    fade.rotation.x = -Math.PI / 2; fade.position.y = 0.001; this.scene.add(fade);
    this.ground = g;
  }

  async loadModel(url, onProgress) {
    const draco = new DRACOLoader();
    draco.setDecoderPath('vendor/three/examples/jsm/libs/draco/gltf/');
    const loader = new GLTFLoader().setDRACOLoader(draco);
    const gltf = await new Promise((res, rej) => loader.load(url, res, (e) => onProgress && onProgress(e.total ? e.loaded / e.total : 0.5), rej));
    this.scene.add(gltf.scene);
    this.model = gltf.scene;
    return gltf.scene;
  }

  setAO(on) {
    this.aoEnabled = on && this.q.ao;
    if (this.aoEnabled && !this.composer) {
      const size = this.renderer.getSize(new THREE.Vector2());
      const rt = new THREE.WebGLRenderTarget(size.x, size.y, { type: THREE.HalfFloatType, samples: 4 });
      this.composer = new EffectComposer(this.renderer, rt);
      this.composer.addPass(new RenderPass(this.scene, this.camera));
      this.gtao = new GTAOPass(this.scene, this.camera, size.x, size.y);
      this.gtao.output = GTAOPass.OUTPUT.Default;
      this.gtao.updateGtaoMaterial({ radius: 0.35, distanceExponent: 1, thickness: 1, scale: 1.2, samples: 12, distanceFallOff: 1, screenSpaceRadius: false });
      this.gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, radiusExponent: 1, rings: 2, samples: 12 });
      this.composer.addPass(this.gtao);
      this.composer.addPass(new OutputPass());
      this.resize();
    }
  }

  resize() {
    const w = this.container.clientWidth, h = this.container.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.labels.setSize(w, h);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
    if (this.composer) { this.composer.setSize(w, h); this.gtao && this.gtao.setSize(w, h); }
  }

  start() {
    const loop = () => {
      const dt = Math.min(0.1, this.clock.getDelta());
      for (const f of this.onFrame) f(dt);
      if (!this.manualCamera) this.controls.update();      // the cockpit camera of the flight mode places itself
      this.renderer.info.reset();
      if (this.composer && this.aoEnabled) this.composer.render(); else this.renderer.render(this.scene, this.camera);
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
