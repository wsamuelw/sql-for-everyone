import * as THREE from 'three';
import { CONFIG } from './config.js';

export const WEAPONS = CONFIG.WEAPONS;

// Beam pool
const beamPool = [];
let currentSpreadBonus = 0;

export function initBeamPool(scene) {
  for (let i = 0; i < CONFIG.BEAM_POOL_SIZE; i++) {
    const geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    const mat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 });
    const line = new THREE.Line(geo, mat);
    line.visible = false;
    scene.add(line);
    beamPool.push({ line, geo, mat, active: false, timer: 0 });
  }
}

function acquireBeam() {
  for (const b of beamPool) {
    if (!b.active) return b;
  }
  return beamPool[0];
}

export function updateBeamPool(delta) {
  for (const b of beamPool) {
    if (!b.active) continue;
    b.timer -= delta;
    if (b.timer <= 0) {
      b.active = false;
      b.line.visible = false;
    } else {
      b.mat.opacity = 0.8 * (b.timer / 0.1);
    }
  }
}

export function resetSpread() { currentSpreadBonus = 0; }

export function updateSpread(delta) {
  currentSpreadBonus = Math.max(0, currentSpreadBonus - CONFIG.SPREAD_RECOVERY * delta);
}

export function fireWeapon(weaponDef, camera, enemies, scene, particles, audio) {
  const origin = new THREE.Vector3();
  camera.getWorldPosition(origin);
  const direction = new THREE.Vector3();
  camera.getWorldDirection(direction);

  const right = new THREE.Vector3();
  right.crossVectors(direction, new THREE.Vector3(0, 1, 0)).normalize();

  let hitAny = false;
  const totalSpread = weaponDef.spread + currentSpreadBonus;

  for (let i = 0; i < weaponDef.rayCount; i++) {
    const dir = direction.clone();
    // Horizontal spread only
    dir.add(right.clone().multiplyScalar((Math.random() - 0.5) * totalSpread * 2));
    dir.normalize();

    const raycaster = new THREE.Raycaster(origin.clone(), dir, 0, 100);
    const meshes = enemies.filter(e => e.alive).map(e => e.mesh);
    const hits = raycaster.intersectObjects(meshes, true);

    if (hits.length > 0) {
      const hit = hits[0];
      const hitEnemy = enemies.find(e => e.mesh === hit.object || e.mesh.children.includes(hit.object));
      if (hitEnemy && hitEnemy.alive) {
        const hitDirection = hit.point.clone().sub(hitEnemy.mesh.position).normalize();
        hitEnemy.takeDamage(weaponDef.damage, hitDirection);
        particles.hitSpark(hit.point, weaponDef.color);
        audio.playHit();
        hitAny = true;
      }
    }

    // Beam visual from pool
    const endPoint = hits.length > 0 ? hits[0].point : origin.clone().add(dir.clone().multiplyScalar(100));
    const beam = acquireBeam();
    const positions = beam.geo.attributes.position.array;
    positions[0] = origin.x; positions[1] = origin.y; positions[2] = origin.z;
    positions[3] = endPoint.x; positions[4] = endPoint.y; positions[5] = endPoint.z;
    beam.geo.attributes.position.needsUpdate = true;
    beam.mat.color.set(weaponDef.color);
    beam.mat.opacity = 0.8;
    beam.line.visible = true;
    beam.active = true;
    beam.timer = 0.1;
  }

  // Progressive spread
  currentSpreadBonus = Math.min(CONFIG.SPREAD_MAX, currentSpreadBonus + CONFIG.SPREAD_INCREASE_PER_SHOT);

  // Muzzle flash + smoke
  const muzzlePos = origin.clone().add(direction.clone().multiplyScalar(1));
  particles.muzzleFlash(muzzlePos, direction, weaponDef.color);
  particles.muzzleSmoke(muzzlePos, direction);
  audio.playShot(WEAPONS.indexOf(weaponDef), origin);

  return hitAny;
}
