import * as THREE from 'three';
import { CONFIG } from './config.js';

function createParticleTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 32;
  canvas.height = 32;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
  gradient.addColorStop(0, 'rgba(255,255,255,1)');
  gradient.addColorStop(0.3, 'rgba(255,255,255,0.6)');
  gradient.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 32, 32);
  return new THREE.CanvasTexture(canvas);
}

export class ParticleSystem {
  constructor(scene) {
    this.scene = scene;
    this.particles = [];
    this.maxParticles = CONFIG.MAX_PARTICLES;
    this.texture = createParticleTexture();

    this.positions = new Float32Array(this.maxParticles * 3);
    this.colors = new Float32Array(this.maxParticles * 3);
    this.sizes = new Float32Array(this.maxParticles);

    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(this.colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(this.sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 0.3,
      map: this.texture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      vertexColors: true,
      sizeAttenuation: true,
    });

    this.points = new THREE.Points(this.geometry, this.material);
    scene.add(this.points);
  }

  emit(position, velocity, count, options = {}) {
    const color = options.color || new THREE.Color(0x00ffff);
    const life = options.life || 0.3;
    const speed = options.speed || 3;
    const size = options.size || 0.3;

    for (let i = 0; i < count; i++) {
      if (this.particles.length >= this.maxParticles) break;
      const dir = new THREE.Vector3(
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2,
      ).normalize();
      this.particles.push({
        position: position.clone(),
        velocity: dir.multiplyScalar(speed).add(velocity || new THREE.Vector3()),
        life,
        maxLife: life,
        color: color.clone(),
        size,
        gravity: options.gravity || 0,
        drag: options.drag || 0,
      });
    }
  }

  muzzleFlash(position, direction, color) {
    this.emit(position, direction.clone().multiplyScalar(15), 5, {
      color: new THREE.Color(color),
      life: 0.05,
      speed: 15,
      size: 0.2,
    });
  }

  muzzleSmoke(position, direction) {
    this.emit(position, direction.clone().multiplyScalar(2), 3, {
      color: new THREE.Color(0x888888),
      life: 0.6,
      speed: 1.5,
      size: 0.15,
      gravity: 0.5,
      drag: 2,
    });
  }

  hitSpark(position, color) {
    this.emit(position, new THREE.Vector3(), 10, {
      color: new THREE.Color(color),
      life: 0.2,
      speed: 5,
      size: 0.15,
    });
  }

  deathExplosion(position, color) {
    this.emit(position, new THREE.Vector3(), 30, {
      color: new THREE.Color(color),
      life: 0.5,
      speed: 4,
      size: 0.4,
    });
  }

  update(delta) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= delta;
      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }
      p.position.add(p.velocity.clone().multiplyScalar(delta));
      p.velocity.y -= p.gravity * delta;
      if (p.drag > 0) {
        p.velocity.multiplyScalar(1 - p.drag * delta);
      }
    }

    for (let i = 0; i < this.maxParticles; i++) {
      if (i < this.particles.length) {
        const p = this.particles[i];
        const alpha = p.life / p.maxLife;
        this.positions[i * 3] = p.position.x;
        this.positions[i * 3 + 1] = p.position.y;
        this.positions[i * 3 + 2] = p.position.z;
        this.colors[i * 3] = p.color.r * alpha;
        this.colors[i * 3 + 1] = p.color.g * alpha;
        this.colors[i * 3 + 2] = p.color.b * alpha;
        this.sizes[i] = p.size * alpha;
      } else {
        this.positions[i * 3] = 0;
        this.positions[i * 3 + 1] = -999;
        this.positions[i * 3 + 2] = 0;
        this.sizes[i] = 0;
      }
    }

    this.geometry.attributes.position.needsUpdate = true;
    this.geometry.attributes.color.needsUpdate = true;
    this.geometry.attributes.size.needsUpdate = true;
  }
}
