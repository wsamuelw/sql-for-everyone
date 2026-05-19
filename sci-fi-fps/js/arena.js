import * as THREE from 'three';
import { CONFIG } from './config.js';

function createGridTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#111';
  ctx.fillRect(0, 0, 256, 256);
  ctx.strokeStyle = '#1a1a2e';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 256; i += 32) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i, 256);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, i);
    ctx.lineTo(256, i);
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(CONFIG.ARENA_SIZE / 4, CONFIG.ARENA_SIZE / 4);
  return texture;
}

export function createArena(scene) {
  const half = CONFIG.ARENA_SIZE / 2;
  const colliders = [];

  // Floor
  const floorGeo = new THREE.PlaneGeometry(CONFIG.ARENA_SIZE, CONFIG.ARENA_SIZE);
  const floorMat = new THREE.MeshStandardMaterial({
    map: createGridTexture(),
    roughness: 0.8,
    metalness: 0.2,
  });
  const floor = new THREE.Mesh(floorGeo, floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  // Walls
  const wallMat = new THREE.MeshStandardMaterial({
    color: 0x222233,
    roughness: 0.4,
    metalness: 0.6,
    transparent: true,
    opacity: 0.6,
  });

  const glowMat = new THREE.MeshStandardMaterial({
    color: 0x00ffff,
    emissive: 0x00ffff,
    emissiveIntensity: 2,
  });

  const wallDefs = [
    { pos: [0, CONFIG.WALL_HEIGHT / 2, -half], size: [CONFIG.ARENA_SIZE, CONFIG.WALL_HEIGHT, 0.5] },
    { pos: [0, CONFIG.WALL_HEIGHT / 2, half], size: [CONFIG.ARENA_SIZE, CONFIG.WALL_HEIGHT, 0.5] },
    { pos: [-half, CONFIG.WALL_HEIGHT / 2, 0], size: [0.5, CONFIG.WALL_HEIGHT, CONFIG.ARENA_SIZE] },
    { pos: [half, CONFIG.WALL_HEIGHT / 2, 0], size: [0.5, CONFIG.WALL_HEIGHT, CONFIG.ARENA_SIZE] },
  ];

  wallDefs.forEach(({ pos, size }) => {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(...size), wallMat);
    wall.position.set(...pos);
    scene.add(wall);

    // Glow edge on top
    const edgeSize = [...size];
    edgeSize[1] = 0.05;
    const edge = new THREE.Mesh(new THREE.BoxGeometry(...edgeSize), glowMat);
    edge.position.set(pos[0], pos[1] + size[1] / 2, pos[2]);
    scene.add(edge);

    // Collider
    colliders.push({
      min: new THREE.Vector3(
        pos[0] - size[0] / 2,
        0,
        pos[2] - size[2] / 2,
      ),
      max: new THREE.Vector3(
        pos[0] + size[0] / 2,
        CONFIG.WALL_HEIGHT,
        pos[2] + size[2] / 2,
      ),
    });
  });

  // Interior obstacles
  const obstacleMat = new THREE.MeshStandardMaterial({
    color: 0x1a1a2e,
    roughness: 0.5,
    metalness: 0.5,
  });

  const obstacles = [
    { pos: [8, 1.5, 8], size: [3, 3, 3] },
    { pos: [-10, 1, -6], size: [4, 2, 2] },
    { pos: [5, 1.5, -12], size: [2, 3, 4] },
    { pos: [-8, 1, 10], size: [3, 2, 3] },
    { pos: [15, 1.5, 0], size: [2, 3, 6] },
    { pos: [-15, 1, -10], size: [5, 2, 2] },
    { pos: [0, 1, 15], size: [6, 2, 2] },
    { pos: [-5, 1.5, -18], size: [3, 3, 3] },
  ];

  obstacles.forEach(({ pos, size }) => {
    const block = new THREE.Mesh(new THREE.BoxGeometry(...size), obstacleMat);
    block.position.set(...pos);
    block.castShadow = true;
    block.receiveShadow = true;
    scene.add(block);

    // Glow edge on top
    const edge = new THREE.Mesh(
      new THREE.BoxGeometry(size[0] + 0.1, 0.05, size[2] + 0.1),
      glowMat,
    );
    edge.position.set(pos[0], pos[1] + size[1] / 2, pos[2]);
    scene.add(edge);

    colliders.push({
      min: new THREE.Vector3(pos[0] - size[0] / 2, 0, pos[2] - size[2] / 2),
      max: new THREE.Vector3(pos[0] + size[0] / 2, size[1], pos[2] + size[2] / 2),
    });
  });

  // Lighting
  scene.add(new THREE.AmbientLight(0x111122, 0.4));

  const pointLights = [
    { pos: [15, 4, 15], color: 0x00ffff, intensity: 80 },
    { pos: [-15, 4, -15], color: 0xff00ff, intensity: 80 },
    { pos: [15, 4, -15], color: 0x0088ff, intensity: 60 },
    { pos: [-15, 4, 15], color: 0xff0088, intensity: 60 },
    { pos: [0, 5, 0], color: 0x4444ff, intensity: 40 },
  ];

  pointLights.forEach(({ pos, color, intensity }) => {
    const light = new THREE.PointLight(color, intensity, 40);
    light.position.set(...pos);
    scene.add(light);
  });

  const spot = new THREE.SpotLight(0xffffff, 30, 50, Math.PI / 6, 0.5);
  spot.position.set(0, 20, 0);
  spot.target.position.set(0, 0, 0);
  spot.castShadow = true;
  spot.shadow.mapSize.width = 1024;
  spot.shadow.mapSize.height = 1024;
  spot.shadow.camera.near = 1;
  spot.shadow.camera.far = 50;
  scene.add(spot);
  scene.add(spot.target);

  // Fog
  scene.fog = new THREE.FogExp2(CONFIG.FOG_COLOR, CONFIG.FOG_DENSITY);

  // Floating decorative shapes
  const decoMat = new THREE.MeshStandardMaterial({
    color: 0x00ffff,
    emissive: 0x00ffff,
    emissiveIntensity: 1,
    wireframe: true,
  });

  const decos = [];
  for (let i = 0; i < 6; i++) {
    const geo = i % 2 === 0
      ? new THREE.OctahedronGeometry(0.5, 0)
      : new THREE.TetrahedronGeometry(0.5, 0);
    const mesh = new THREE.Mesh(geo, decoMat);
    mesh.position.set(
      (Math.random() - 0.5) * 40,
      3 + Math.random() * 3,
      (Math.random() - 0.5) * 40,
    );
    scene.add(mesh);
    decos.push(mesh);
  }

  return { colliders, decos };
}
