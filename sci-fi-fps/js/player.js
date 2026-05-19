import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { CONFIG } from './config.js';
import { isKeyDown } from './input.js';
import { fireWeapon, WEAPONS } from './weapons.js';

export class Player {
  constructor(camera, scene) {
    this.camera = camera;
    this.scene = scene;
    this.controls = new PointerLockControls(camera, document.body);

    this.health = CONFIG.PLAYER_MAX_HEALTH;
    this.maxHealth = CONFIG.PLAYER_MAX_HEALTH;
    this.alive = true;

    this.position = new THREE.Vector3(0, CONFIG.PLAYER_HEIGHT, 0);
    camera.position.copy(this.position);

    this.velocity = new THREE.Vector3();
    this.bobTime = 0;
    this.bobAmount = 0;
    this.prevBobCycle = 0;

    this.currentWeapon = 0;
    this.fireCooldown = 0;
    this.ammo = WEAPONS.map(w => w.ammoMax);

    // Weapon sway
    this.swayTime = 0;
    this.swayTarget = new THREE.Vector3();
    this.swayCurrent = new THREE.Vector3();

    // Recoil
    this.recoilPitch = 0;

    // Reload
    this.isReloading = false;
    this.reloadTimer = 0;

    // Screen shake
    this.shakeIntensity = 0;
    this.shakeDecay = CONFIG.SHAKE_DAMAGE_DECAY;
    this.shakeOffset = new THREE.Euler();

    // FOV
    this.targetFOV = CONFIG.FOV_NORMAL;

    // Gun mesh
    this.gunGroup = new THREE.Group();
    const gunMat = new THREE.MeshStandardMaterial({
      color: 0x333344,
      emissive: 0x00ffff,
      emissiveIntensity: 0.5,
      metalness: 0.8,
      roughness: 0.2,
    });

    // Body
    const gunBody = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.05, 0.4), gunMat);
    this.gunGroup.add(gunBody);

    // Barrel
    const barrel = new THREE.Mesh(
      new THREE.CylinderGeometry(0.015, 0.015, 0.2, 8),
      new THREE.MeshStandardMaterial({ color: 0x222233, emissive: 0x00ffff, emissiveIntensity: 0.3 }),
    );
    barrel.rotation.x = Math.PI / 2;
    barrel.position.z = -0.3;
    this.gunGroup.add(barrel);

    // Scope
    const scope = new THREE.Mesh(
      new THREE.BoxGeometry(0.03, 0.03, 0.12),
      new THREE.MeshStandardMaterial({ color: 0x222233, emissive: 0x00ffff, emissiveIntensity: 0.2 }),
    );
    scope.position.set(0, 0.04, -0.15);
    this.gunGroup.add(scope);

    // Grip
    const grip = new THREE.Mesh(
      new THREE.BoxGeometry(0.03, 0.08, 0.04),
      new THREE.MeshStandardMaterial({ color: 0x222233, metalness: 0.8, roughness: 0.3 }),
    );
    grip.position.set(0, -0.05, -0.05);
    grip.rotation.x = 0.3;
    this.gunGroup.add(grip);

    // Trigger guard
    const guard = new THREE.Mesh(
      new THREE.TorusGeometry(0.02, 0.003, 4, 8, Math.PI),
      new THREE.MeshStandardMaterial({ color: 0x333344 }),
    );
    guard.position.set(0, -0.03, -0.08);
    guard.rotation.x = Math.PI / 2;
    this.gunGroup.add(guard);

    // Side panel detail
    const panel = new THREE.Mesh(
      new THREE.BoxGeometry(0.005, 0.03, 0.15),
      new THREE.MeshStandardMaterial({ color: 0x00ffff, emissive: 0x00ffff, emissiveIntensity: 1 }),
    );
    panel.position.set(0.028, 0, -0.1);
    this.gunGroup.add(panel);

    this.gunGroup.position.set(0.25, -0.2, -0.5);
    camera.add(this.gunGroup);
    scene.add(camera);
  }

  lock() {
    this.controls.lock();
  }

  get isLocked() {
    return this.controls.isLocked;
  }

  switchWeapon(index) {
    if (index >= 0 && index < WEAPONS.length) {
      this.currentWeapon = index;
    }
  }

  startReload() {
    if (this.isReloading) return;
    const weapon = WEAPONS[this.currentWeapon];
    if (this.ammo[this.currentWeapon] >= weapon.ammoMax) return;
    this.isReloading = true;
    this.reloadTimer = CONFIG.RELOAD_TIME[this.currentWeapon];
  }

  shoot(enemies, particles, audio) {
    if (!this.alive || this.fireCooldown > 0 || this.isReloading) return null;
    if (this.ammo[this.currentWeapon] <= 0) return null;

    const weapon = WEAPONS[this.currentWeapon];
    this.fireCooldown = 1 / weapon.fireRate;
    this.ammo[this.currentWeapon]--;

    fireWeapon(weapon, this.camera, enemies, this.scene, particles, audio);

    // Recoil on gun model
    this.recoilPitch += CONFIG.RECOIL_PITCH;

    // Camera micro-shake
    this.shakeIntensity += CONFIG.SHAKE_SHOOT_INTENSITY;
    this.shakeDecay = CONFIG.SHAKE_SHOOT_DECAY;

    return weapon;
  }

  takeDamage(amount, audio) {
    if (!this.alive) return;
    this.health -= amount;
    audio.playDamage();
    this.shakeIntensity += CONFIG.SHAKE_DAMAGE_INTENSITY;
    this.shakeDecay = CONFIG.SHAKE_DAMAGE_DECAY;
    if (this.health <= 0) {
      this.health = 0;
      this.alive = false;
    }
  }

  update(delta, input, colliders, audio) {
    if (!this.alive) return;
    this.fireCooldown = Math.max(0, this.fireCooldown - delta);

    // Reload update
    if (this.isReloading) {
      this.reloadTimer -= delta;
      const progress = 1 - (this.reloadTimer / CONFIG.RELOAD_TIME[this.currentWeapon]);
      const dip = Math.sin(progress * Math.PI) * CONFIG.RELOAD_DIP;
      this.gunGroup.position.y = -0.2 - dip;
      if (this.reloadTimer <= 0) {
        this.isReloading = false;
        this.ammo[this.currentWeapon] = WEAPONS[this.currentWeapon].ammoMax;
        this.gunGroup.position.y = -0.2;
      }
    }

    // Movement
    const speed = isKeyDown('ShiftLeft')
      ? CONFIG.PLAYER_SPEED * CONFIG.PLAYER_SPRINT_MULTIPLIER
      : CONFIG.PLAYER_SPEED;

    const direction = new THREE.Vector3();
    const forward = new THREE.Vector3();
    this.camera.getWorldDirection(forward);
    forward.y = 0;
    forward.normalize();

    const right = new THREE.Vector3();
    right.crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();

    if (isKeyDown('KeyW')) direction.add(forward);
    if (isKeyDown('KeyS')) direction.sub(forward);
    if (isKeyDown('KeyA')) direction.sub(right);
    if (isKeyDown('KeyD')) direction.add(right);

    const isMoving = direction.length() > 0;
    if (isMoving) {
      direction.normalize();
      this.position.x += direction.x * speed * delta;
      this.position.z += direction.z * speed * delta;
    }

    // Clamp to arena
    const bound = CONFIG.ARENA_SIZE / 2 - 1;
    this.position.x = Math.max(-bound, Math.min(bound, this.position.x));
    this.position.z = Math.max(-bound, Math.min(bound, this.position.z));

    // Wall collision
    if (colliders) {
      const playerRadius = 0.4;
      for (const col of colliders) {
        const closestX = Math.max(col.min.x, Math.min(this.position.x, col.max.x));
        const closestZ = Math.max(col.min.z, Math.min(this.position.z, col.max.z));
        const dx = this.position.x - closestX;
        const dz = this.position.z - closestZ;
        const dist = Math.sqrt(dx * dx + dz * dz);
        if (dist < playerRadius) {
          const pushX = dist > 0 ? dx / dist : 1;
          const pushZ = dist > 0 ? dz / dist : 0;
          this.position.x = closestX + pushX * playerRadius;
          this.position.z = closestZ + pushZ * playerRadius;
        }
      }
    }

    // Head bob + footstep detection
    const prevBob = Math.floor(this.bobTime);
    if (isMoving) {
      this.bobTime += delta * (isKeyDown('ShiftLeft') ? 12 : 8);
      this.bobAmount = Math.sin(this.bobTime) * 0.04;
    } else {
      this.bobAmount *= 0.9;
    }
    const newBob = Math.floor(this.bobTime);
    if (isMoving && newBob !== prevBob && audio) {
      audio.playFootstep();
    }

    // Weapon sway
    this.swayTime += delta;
    const idleSwayX = Math.sin(this.swayTime * CONFIG.SWAY_IDLE_SPEED) * CONFIG.SWAY_IDLE_AMOUNT;
    const idleSwayY = Math.cos(this.swayTime * CONFIG.SWAY_IDLE_SPEED * 0.7) * CONFIG.SWAY_IDLE_AMOUNT;
    const moveSwayX = isMoving ? -direction.x * CONFIG.SWAY_MOVE_AMOUNT : 0;
    this.swayTarget.set(idleSwayX + moveSwayX, idleSwayY, 0);
    this.swayCurrent.lerp(this.swayTarget, delta * 8);

    // Apply sway + recoil to gun
    this.gunGroup.rotation.x = this.swayCurrent.y;
    this.gunGroup.rotation.z = this.swayCurrent.x;
    if (this.recoilPitch !== 0) {
      this.recoilPitch *= Math.pow(0.01, delta * CONFIG.RECOIL_RECOVERY);
      if (Math.abs(this.recoilPitch) < 0.001) this.recoilPitch = 0;
      this.gunGroup.rotation.x += this.recoilPitch;
    }

    // Screen shake
    if (this.shakeIntensity > 0.001) {
      this.shakeOffset.set(
        (Math.random() - 0.5) * this.shakeIntensity,
        (Math.random() - 0.5) * this.shakeIntensity,
        0,
      );
      this.shakeIntensity *= Math.pow(0.01, delta * this.shakeDecay);
    } else {
      this.shakeOffset.set(0, 0, 0);
      this.shakeIntensity = 0;
    }

    // Camera position
    this.camera.position.set(
      this.position.x,
      CONFIG.PLAYER_HEIGHT + this.bobAmount,
      this.position.z,
    );

    // Apply shake offset to camera rotation
    this.camera.rotation.x += this.shakeOffset.x;
    this.camera.rotation.y += this.shakeOffset.y;

    // FOV
    this.targetFOV = isKeyDown('ShiftLeft') ? CONFIG.FOV_SPRINT : CONFIG.FOV_NORMAL;
    this.camera.fov = THREE.MathUtils.lerp(this.camera.fov, this.targetFOV, delta * CONFIG.FOV_LERP_SPEED);
    this.camera.updateProjectionMatrix();
  }

  respawn() {
    this.health = this.maxHealth;
    this.alive = true;
    this.position.set(0, CONFIG.PLAYER_HEIGHT, 0);
    this.camera.position.copy(this.position);
    this.ammo = WEAPONS.map(w => w.ammoMax);
    this.currentWeapon = 0;
    this.isReloading = false;
    this.recoilPitch = 0;
    this.shakeIntensity = 0;
    this.camera.fov = CONFIG.FOV_NORMAL;
    this.camera.updateProjectionMatrix();
  }
}
