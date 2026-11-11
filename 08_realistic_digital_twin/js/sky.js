// The sky and the apron of the viewer, drawn by the program: no photograph, nothing downloaded.
//
// The sky is a dome with a small shader: a gradient from the horizon to the zenith, the sun with its glow, and
// fair-weather clouds lit from the sun's side. The apron is a painted texture of concrete slabs with joints,
// stains and a taxi line. Both are illustrations of a clear day at an airfield, not a place.
import * as THREE from 'three';

const SKY_VERTEX = /* glsl */`
  varying vec3 vDir;
  void main() {
    vDir = normalize(position);
    vec4 p = modelViewMatrix * vec4(position, 0.0);      // the dome goes with the camera: only its direction counts
    gl_Position = projectionMatrix * vec4(p.xyz, 1.0);
    gl_Position.z = gl_Position.w;                       // on the far plane, behind everything
  }`;

const SKY_FRAGMENT = /* glsl */`
  uniform vec3 sunDir; uniform vec3 zenith; uniform vec3 horizon; uniform vec3 haze; uniform vec3 ground;
  uniform float clouds; uniform float time;
  varying vec3 vDir;
  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
  }
  float fbm(vec2 p) { float a = 0.5, s = 0.0; for (int i = 0; i < 5; i++) { s += a * noise(p); p = p * 2.03 + vec2(17.0, 9.0); a *= 0.5; } return s; }
  void main() {
    vec3 d = normalize(vDir);
    float up = max(d.y, 0.0);
    // clear sky: pale at the horizon, deep overhead
    vec3 col = mix(horizon, zenith, pow(up, 0.42));
    col = mix(haze, col, smoothstep(0.0, 0.16, up));
    // the sun and the brightness round it
    float c = max(dot(d, sunDir), 0.0);
    col += vec3(1.0, 0.93, 0.80) * (pow(c, 6.0) * 0.16 + pow(c, 48.0) * 0.5 + smoothstep(0.99975, 0.99992, c) * 30.0);
    // fair-weather clouds on a flat layer: brighter on the sun's side, grey under
    if (d.y > 0.02 && clouds > 0.0) {
      vec2 p = d.xz / (d.y + 0.10) * 0.55 + vec2(time * 0.004, 3.0);
      float n = fbm(p * 1.6) * 0.65 + fbm(p * 5.3 + 11.0) * 0.35;
      float cover = smoothstep(1.0 - clouds, 1.0 - clouds + 0.20, n);
      float lit = 0.72 + 0.28 * smoothstep(-0.2, 0.9, dot(normalize(vec3(d.x, 0.35, d.z)), sunDir));
      float under = smoothstep(1.0 - clouds + 0.05, 1.0 - clouds + 0.38, n);      // the thick middle of a cloud is darker
      vec3 cloud = mix(vec3(1.0, 0.99, 0.97) * lit * 1.25, vec3(0.62, 0.66, 0.74), under * 0.55);
      col = mix(col, cloud, cover * smoothstep(0.02, 0.22, d.y) * 0.92);
    }
    // below the horizon: the haze of the far ground
    col = mix(col, ground, smoothstep(0.0, -0.06, d.y));
    gl_FragColor = vec4(col, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }`;

/** A sky dome that follows the camera. sun: a unit vector toward the sun. */
export function createSky(sun, { clouds = 0.52 } = {}) {
  const material = new THREE.ShaderMaterial({
    vertexShader: SKY_VERTEX, fragmentShader: SKY_FRAGMENT, side: THREE.BackSide, depthWrite: false, depthTest: true, fog: false,
    uniforms: {
      sunDir: { value: sun.clone().normalize() }, clouds: { value: clouds }, time: { value: 0 },
      zenith: { value: new THREE.Color(0.10, 0.27, 0.66) }, horizon: { value: new THREE.Color(0.50, 0.68, 0.92) },
      haze: { value: new THREE.Color(0.74, 0.82, 0.91) }, ground: { value: new THREE.Color(0.60, 0.64, 0.66) },
    },
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 24), material);
  dome.name = '_sky'; dome.frustumCulled = false; dome.renderOrder = -100; dome.raycast = () => {};
  return dome;
}
/** The colour of the far haze, for the fog that fades the ground into the sky. */
export const HAZE = 0xbdd1e8;

// ---------------------------------------------------------------------------------------------- the apron
function seeded(seed) { let s = seed >>> 0; return () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; }; }

/**
 * Concrete slabs: { map, roughnessMap, normalMap }, one tile of `slabs` x `slabs` slabs. Painted on canvases.
 * The joints are sealed dark, each slab has its own tone, and there are stains and tyre marks.
 */
export function apronTextures(size = 2048, slabs = 4) {
  const rnd = seeded(1979);
  const make = () => { const c = document.createElement('canvas'); c.width = c.height = size; return c; };
  const colour = make(), rough = make(), height = make();
  const g = colour.getContext('2d'), r = rough.getContext('2d'), h = height.getContext('2d');
  const cell = size / slabs;
  g.fillStyle = '#7b7973'; g.fillRect(0, 0, size, size);
  r.fillStyle = '#d8d8d8'; r.fillRect(0, 0, size, size);
  h.fillStyle = '#808080'; h.fillRect(0, 0, size, size);
  for (let i = 0; i < slabs; i++) for (let j = 0; j < slabs; j++) {      // each slab was poured on its own day
    const v = 112 + Math.floor(rnd() * 22), warm = Math.floor(rnd() * 8);
    g.fillStyle = `rgb(${v + warm}, ${v + warm - 2}, ${v - 4})`;
    g.fillRect(i * cell, j * cell, cell, cell);
  }
  // the grain of brushed concrete, and the dirt that gathers on it
  const img = g.getImageData(0, 0, size, size), d = img.data;
  for (let p = 0; p < d.length; p += 4) { const n = (rnd() - 0.5) * 22; d[p] += n; d[p + 1] += n; d[p + 2] += n; }
  g.putImageData(img, 0, 0);
  const blot = (ctx, x, y, radius, rgba) => { const grad = ctx.createRadialGradient(x, y, 0, x, y, radius); grad.addColorStop(0, rgba); grad.addColorStop(1, rgba.replace(/[\d.]+\)$/, '0)')); ctx.fillStyle = grad; ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2); };
  for (let k = 0; k < 90; k++) blot(g, rnd() * size, rnd() * size, 40 + rnd() * 260, `rgba(${rnd() > 0.5 ? '60,58,54' : '176,172,164'},${0.03 + rnd() * 0.06})`);
  for (let k = 0; k < 14; k++) { const x = rnd() * size, y = rnd() * size, rad = 14 + rnd() * 50; blot(g, x, y, rad, `rgba(28,26,24,${0.25 + rnd() * 0.3})`); blot(r, x, y, rad, 'rgba(70,70,70,0.7)'); }      // oil: dark and smooth
  // tyre marks: long faint streaks, mostly one way
  g.lineCap = 'round';
  for (let k = 0; k < 26; k++) {
    const x = rnd() * size, y = rnd() * size, len = 200 + rnd() * 700, a = (rnd() - 0.5) * 0.5 + (rnd() > 0.8 ? 1.3 : 0);
    g.strokeStyle = `rgba(30,30,30,${0.04 + rnd() * 0.07})`; g.lineWidth = 6 + rnd() * 10;
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * len * 0.5 + (rnd() - 0.5) * 60, y + Math.sin(a) * len * 0.5 + (rnd() - 0.5) * 60, x + Math.cos(a) * len, y + Math.sin(a) * len); g.stroke();
  }
  // hairline cracks: each wanders in one general direction
  g.strokeStyle = 'rgba(40,38,36,0.22)'; g.lineWidth = Math.max(0.6, size / 2600);
  h.strokeStyle = '#6a6a6a'; h.lineWidth = Math.max(0.8, size / 2000);
  for (let k = 0; k < 16; k++) {
    let x = rnd() * size, y = rnd() * size, a = rnd() * Math.PI * 2; g.beginPath(); h.beginPath(); g.moveTo(x, y); h.moveTo(x, y);
    for (let s = 0; s < 40; s++) { a += (rnd() - 0.5) * 0.7; x += Math.cos(a) * size / 170; y += Math.sin(a) * size / 170; g.lineTo(x, y); h.lineTo(x, y); }
    g.stroke(); h.stroke();
  }
  // the joints, sealed with dark compound: they wrap, so the tiles join
  for (const [ctx, style, width] of [[g, '#4a4743', Math.max(2, size / 700)], [r, '#9c9c9c', Math.max(2, size / 700)], [h, '#303030', Math.max(3, size / 560)]]) {
    ctx.strokeStyle = style; ctx.lineWidth = width; ctx.beginPath();
    for (let i = 0; i <= slabs; i++) { ctx.moveTo(i * cell, 0); ctx.lineTo(i * cell, size); ctx.moveTo(0, i * cell); ctx.lineTo(size, i * cell); }
    ctx.stroke();
  }
  // a normal map from the height canvas (joints and cracks are below the surface)
  const hd = h.getImageData(0, 0, size, size).data, nimg = h.createImageData(size, size), nd = nimg.data;
  const at = (x, y) => hd[(((y + size) % size) * size + ((x + size) % size)) * 4];
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const dx = (at(x + 1, y) - at(x - 1, y)) / 255, dy = (at(x, y + 1) - at(x, y - 1)) / 255, k = 2.2;
    const nx = -dx * k, ny = dy * k, nz = 1, l = Math.hypot(nx, ny, nz), p = (y * size + x) * 4;
    nd[p] = (nx / l * 0.5 + 0.5) * 255; nd[p + 1] = (ny / l * 0.5 + 0.5) * 255; nd[p + 2] = (nz / l * 0.5 + 0.5) * 255; nd[p + 3] = 255;
  }
  const normal = make(); normal.getContext('2d').putImageData(nimg, 0, 0);
  const tex = (canvas, srgb) => { const t = new THREE.CanvasTexture(canvas); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 16; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  return { map: tex(colour, true), roughnessMap: tex(rough, false), normalMap: tex(normal, false) };
}

/** Painted markings of a parking stand: a yellow lead-in line that passes under the nose wheel, and a stop bar. Returns a mesh. */
export function standMarkings() {
  const c = document.createElement('canvas'); c.width = 512; c.height = 2048;
  const g = c.getContext('2d'), rnd = seeded(7);
  g.clearRect(0, 0, 512, 2048);
  g.strokeStyle = '#d9b21f'; g.lineWidth = 15; g.lineCap = 'butt';
  g.beginPath(); g.moveTo(256, 2048); g.lineTo(256, 610); g.stroke();                       // the lead-in line (0.15 m wide)
  g.beginPath(); g.moveTo(256 - 110, 610); g.lineTo(256 + 110, 610); g.stroke();            // the stop bar
  // worn paint: bites out of it
  g.globalCompositeOperation = 'destination-out';
  for (let k = 0; k < 2600; k++) { g.fillStyle = `rgba(0,0,0,${0.25 + rnd() * 0.6})`; const s = 1 + rnd() * 5; g.fillRect(256 - 130 + rnd() * 260, 560 + rnd() * 1490, s, s * (0.5 + rnd())); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 16;
  // the canvas is 5.12 m by 20.48 m of apron (100 px a metre); the stop bar lies a little ahead of the nose wheel
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(5.12, 20.48), new THREE.MeshStandardMaterial({ map: t, transparent: true, roughness: 0.8, metalness: 0, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }));
  mesh.rotation.x = -Math.PI / 2; mesh.rotation.z = Math.PI;      // the top of the canvas toward the nose (+Z)
  mesh.userData.barAhead = 10.24 - 6.1;                           // the stop bar is this far ahead of the middle of the canvas
  mesh.position.set(0, 0.004, 1.0 - mesh.userData.barAhead);
  mesh.receiveShadow = true; mesh.name = '_stand'; mesh.renderOrder = 1; mesh.raycast = () => {};
  return mesh;
}
