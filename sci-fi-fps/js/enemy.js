import * as THREE from 'three';
import { CONFIG } from './config.js';

const CHASE = 0;
const ATTACK = 1;
const DYING = 2;

const spawnPoints = [];
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  spawnPoints.push(new THREE.Vector3(
    Math.cos(angle) * (CONFIG.ARENA_SIZE / 2 - 5),
    0,
    Math.sin(angle) * (CONFIG.ARENA_SIZE / 2 - 5),
  ));
}

export class Enemy {
  constructor(scene, position, wave) {
    this.scene = scene;
    this.alive = true;
    this.state = CHASE;
    this.attackTimer = 0;
    this.audio = null;
    this.particles = null;

    // Hit reaction state
    this.flinchTimer = 0;
    this.flinchDirection = new THREE.Vector3();
    this.staggerTimer = 0;
    this.tumbleRotation = new THREE.Vector3();

    // Flanking state
    this.isFlanking = false;
    this.flankTimer = 0;
    this.flankTarget = null;

    const healthScale = 1 + (wave - 1) * 0.2;
    const speedScale = 1 + (wave - 1) * 0.1;
    this.health = CONFIG.ENEMY_BASE_HEALTH * healthScale;
    this.maxHealth = this.health;
    this.speed = CONFIG.ENEMY_BASE_SPEED * speedScale;

    // Build mesh
    this.mesh = new THREE.Group();

    // Body
    const bodyGeo = new THREE.IcosahedronGeometry(0.5, 0);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0xff2200,
      emissive: 0xff2200,
      emissiveIntensity: 0.8,
      roughness: 0.3,
      metalness: 0.7,
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 1.2;
    this.mesh.add(body);

    // Head
    const headGeo = new THREE.BoxGeometry(0.3, 0.3, 0.3);
    const headMat = new THREE.MeshStandardMaterial({
      color: 0xff4400,
      emissive: 0xff4400,
      emissiveIntensity: 1,
    });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 2;
    this.mesh.add(head);

    // Eyes
    const eyeGeo = new THREE.BoxGeometry(0.08, 0.06, 0.05);
    const eyeMat = new THREE.MeshStandardMaterial({
      color: 0xffff00,
      emissive: 0xffff00,
      emissiveIntensity: 3,
    });
    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.08, 2.02, 0.16);
    this.mesh.add(leftEye);
    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.08, 2.02, 0.16);
    this.mesh.add(rightEye);

    // Arms (indices 4 and 5)
    const armGeo = new THREE.BoxGeometry(0.1, 0.6, 0.1);
    const armMat = new THREE.MeshStandardMaterial({
      color: 0xcc1100,
      emissive: 0xcc1100,
      emissiveIntensity: 0.5,
    });
    const leftArm = new THREE.Mesh(armGeo, armMat);
    leftArm.position.set(-0.65, 1.2, 0);
    this.mesh.add(leftArm);
    const rightArm = new THREE.Mesh(armGeo, armMat);
    rightArm.position.set(0.65, 1.2, 0);
    this.mesh.add(rightArm);

    // Glow light
    const light = new THREE.PointLight(0xff2200, 5, 5);
    light.position.y = 1.5;
    this.mesh.add(light);

    this.mesh.position.copy(position);
    scene.add(this.mesh);
  }

  takeDamage(amount, hitDirection) {
    if (!this.alive) return;
    this.health -= amount;

    // Flash white briefly
    this.mesh.children[0].material.emissiveIntensity = 3;
    setTimeout(() => {
      if (this.mesh.children[0]) {
        this.mesh.children[0].material.emissiveIntensity = 0.8;
      }
    }, 50);

    // Flinch — brief pushback
    if (hitDirection) {
      this.flinchDirection.copy(hitDirection).normalize().negate();
      this.flinchTimer = 0.15;
    }

    // Stagger on high damage
    if (amount >= CONFIG.ENEMY_KNOCKBACK_THRESHOLD) {
      this.staggerTimer = CONFIG.ENEMY_STAGGER_DURATION;
      if (hitDirection) {
        this.mesh.position.add(
          hitDirection.clone().normalize().negate().multiplyScalar(CONFIG.ENEMY_KNOCKBACK_FORCE * 0.1),
        );
      }
    }

    // Play screech
    if (this.audio) {
      this.audio.playEnemyScreech(this.mesh.position);
    }

    if (this.health <= 0) {
      this.die();
    }
  }

  die() {
    this.alive = false;
    this.state = DYING;

    // Death explosion particles
    if (this.particles) {
      this.particles.deathExplosion(
        this.mesh.position.clone().add(new THREE.Vector3(0, 1, 0)),
        0xff2200,
      );
    }

    // Death sounds
    if (this.audio) {
      this.audio.playExplosion();
      this.audio.playEnemyDeathScream(this.mesh.position);
    }

    // Tumble rotation
    this.tumbleRotation.set(
      (Math.random() - 0.5) * CONFIG.ENEMY_DEATH_TUMBLE_SPEED,
      (Math.random() - 0.5) * CONFIG.ENEMY_DEATH_TUMBLE_SPEED,
      (Math.random() - 0.5) * CONFIG.ENEMY_DEATH_TUMBLE_SPEED,
    );
  }

  update(delta, playerPos, colliders) {
    if (!this.alive && this.state !== DYING) return;

    // Dying state — tumble and shrink
    if (this.state === DYING) {
      const scale = this.mesh.scale.x - delta * 3;
      if (scale <= 0) {
        this.scene.remove(this.mesh);
        return false;
      }
      this.mesh.scale.setScalar(scale);
      this.mesh.rotation.x += this.tumbleRotation.x * delta;
      this.mesh.rotation.y += this.tumbleRotation.y * delta;
      this.mesh.rotation.z += this.tumbleRotation.z * delta;
      return true;
    }

    // Flinch
    if (this.flinchTimer > 0) {
      this.flinchTimer -= delta;
      this.mesh.position.add(this.flinchDirection.clone().multiplyScalar(CONFIG.ENEMY_FLINCH_STRENGTH * delta));
    }

    // Stagger tilt
    if (this.staggerTimer > 0) {
      this.staggerTimer -= delta;
      this.mesh.rotation.x = Math.sin(this.staggerTimer * 20) * 0.3;
    } else {
      this.mesh.rotation.x *= 0.9;
    }

    // Calculate direction to player
    const toPlayer = new THREE.Vector3().subVectors(playerPos, this.mesh.position);
    toPlayer.y = 0;
    const distance = toPlayer.length();
    toPlayer.normalize();

    // Alert radius — idle if player is far
    if (distance > CONFIG.ENEMY_ALERT_RADIUS) {
      this.mesh.children[0].rotation.y += delta * 0.5;
      return true;
    }

    // Rotate toward player
    const targetAngle = Math.atan2(toPlayer.x, toPlayer.z);
    let currentAngle = this.mesh.rotation.y;
    let angleDiff = targetAngle - currentAngle;
    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
    this.mesh.rotation.y += angleDiff * delta * 5;

    if (distance < CONFIG.ENEMY_ATTACK_RANGE) {
      this.state = ATTACK;

      // Arm swing animation
      const swingProgress = 1 - (this.attackTimer / CONFIG.ENEMY_ATTACK_COOLDOWN);
      const swingAngle = Math.sin(swingProgress * Math.PI) * 1.2;
      if (this.mesh.children[4]) this.mesh.children[4].rotation.x = -swingAngle;
      if (this.mesh.children[5]) this.mesh.children[5].rotation.x = -swingAngle;

      this.attackTimer -= delta;
      if (this.attackTimer <= 0) {
        this.attackTimer = CONFIG.ENEMY_ATTACK_COOLDOWN;
        return 'attack';
      }
    } else {
      this.state = CHASE;

      // Reset arm rotation
      if (this.mesh.children[4]) this.mesh.children[4].rotation.x = 0;
      if (this.mesh.children[5]) this.mesh.children[5].rotation.x = 0;

      // Flanking behaviour
      let target = playerPos.clone();
      if (this.isFlanking) {
        this.flankTimer -= delta;
        if (this.flankTimer <= 0) {
          this.isFlanking = false;
        } else if (this.flankTarget) {
          target = this.flankTarget.clone();
        }
      } else if (Math.random() < CONFIG.ENEMY_FLANK_CHANCE * delta) {
        const flankAngle = Math.random() * Math.PI * 2;
        const flankDist = 5 + Math.random() * 5;
        this.flankTarget = playerPos.clone();
        this.flankTarget.x += Math.cos(flankAngle) * flankDist;
        this.flankTarget.z += Math.sin(flankAngle) * flankDist;
        this.isFlanking = true;
        this.flankTimer = 2;
        target = this.flankTarget.clone();
      }

      // Recalculate direction to (possibly flanking) target
      const toTarget = new THREE.Vector3().subVectors(target, this.mesh.position);
      toTarget.y = 0;
      toTarget.normalize();

      // Obstacle avoidance — steer away from arena walls
      const nextPos = this.mesh.position.clone().add(toTarget.clone().multiplyScalar(this.speed * delta));
      const halfArena = CONFIG.ARENA_SIZE / 2 - 2;
      if (Math.abs(nextPos.x) > halfArena || Math.abs(nextPos.z) > halfArena) {
        toTarget.x += (Math.random() - 0.5) * 2;
        toTarget.z += (Math.random() - 0.5) * 2;
        toTarget.normalize();
      }

      // Collider avoidance
      if (colliders) {
        for (const col of colliders) {
          const closestX = Math.max(col.min.x, Math.min(nextPos.x, col.max.x));
          const closestZ = Math.max(col.min.z, Math.min(nextPos.z, col.max.z));
          const dx = nextPos.x - closestX;
          const dz = nextPos.z - closestZ;
          const dist = Math.sqrt(dx * dx + dz * dz);
          if (dist < 1.0) {
            const pushDir = dist > 0.01
              ? new THREE.Vector3(dx, 0, dz).normalize()
              : new THREE.Vector3(Math.random() - 0.5, 0, Math.random() - 0.5).normalize();
            toTarget.add(pushDir.multiplyScalar(2));
            toTarget.normalize();
          }
        }
      }

      const moveDir = toTarget.multiplyScalar(this.speed * delta);
      this.mesh.position.add(moveDir);
    }

    // Keep on ground
    this.mesh.position.y = 0;

    // Bobbing animation
    this.mesh.children[0].rotation.y += delta * 2;

    return true;
  }

  dispose() {
    this.scene.remove(this.mesh);
  }
}

export class EnemyManager {
  constructor(scene) {
    this.scene = scene;
    this.enemies = [];
    this.wave = 0;
    this.waveTimer = 0;
    this.waveActive = false;
    this.score = 0;
    this.waveBreak = false;
  }

  startWave(waveNum, audio, particles) {
    this.wave = waveNum;
    this.waveActive = true;
    const count = CONFIG.BASE_ENEMY_COUNT + (waveNum - 1) * CONFIG.ENEMIES_PER_WAVE;

    for (let i = 0; i < count; i++) {
      const spawnIdx = i % spawnPoints.length;
      const pos = spawnPoints[spawnIdx].clone();
      pos.x += (Math.random() - 0.5) * 3;
      pos.z += (Math.random() - 0.5) * 3;
      const enemy = new Enemy(this.scene, pos, waveNum);
      enemy.audio = audio;
      enemy.particles = particles;
      this.enemies.push(enemy);
    }

    audio.playWaveStart();
  }

  update(delta, playerPos, particles, audio, colliders) {
    let playerAttacked = false;

    for (let i = this.enemies.length - 1; i >= 0; i--) {
      const result = this.enemies[i].update(delta, playerPos, colliders);
      if (result === false) {
        this.enemies.splice(i, 1);
      } else if (result === 'attack') {
        playerAttacked = true;
      }
    }

    // Separation force between enemies
    for (let i = 0; i < this.enemies.length; i++) {
      for (let j = i + 1; j < this.enemies.length; j++) {
        const a = this.enemies[i];
        const b = this.enemies[j];
        if (!a.alive || !b.alive) continue;
        const diff = new THREE.Vector3().subVectors(a.mesh.position, b.mesh.position);
        diff.y = 0;
        const dist = diff.length();
        if (dist < 1.5 && dist > 0.01) {
          const push = diff.normalize().multiplyScalar(delta * 2);
          a.mesh.position.add(push);
          b.mesh.position.sub(push);
        }
      }
    }

    return playerAttacked;
  }

  getAliveEnemies() {
    return this.enemies.filter(e => e.alive);
  }

  allDead() {
    return this.enemies.length === 0 && this.waveActive;
  }

  addScore(points) {
    this.score += points;
  }

  reset() {
    this.enemies.forEach(e => e.dispose());
    this.enemies = [];
    this.wave = 0;
    this.waveActive = false;
    this.score = 0;
  }
}
