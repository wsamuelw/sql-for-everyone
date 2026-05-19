import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { CONFIG } from './config.js';
import { setupInput, isKeyDown, inputState } from './input.js';
import { AudioManager } from './audio.js';
import { ParticleSystem } from './particles.js';
import { createArena } from './arena.js';
import { Player } from './player.js';
import { EnemyManager } from './enemy.js';
import { WEAPONS, initBeamPool, updateBeamPool, updateSpread } from './weapons.js';
import { HUD } from './hud.js';

// State machine
const MENU = 0;
const PLAYING = 1;
const GAME_OVER = 2;

let state = MENU;

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(CONFIG.FOG_COLOR);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Camera & Scene
const camera = new THREE.PerspectiveCamera(CONFIG.FOV_NORMAL, window.innerWidth / window.innerHeight, 0.1, 1000);
const scene = new THREE.Scene();

// Post-processing
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.8,  // strength
  0.4,  // radius
  0.85, // threshold
);
composer.addPass(bloomPass);
composer.addPass(new OutputPass());

// Systems
setupInput();
const audio = new AudioManager();
const particles = new ParticleSystem(scene);
const { colliders, decos } = createArena(scene);
initBeamPool(scene);
const player = new Player(camera, scene);
const enemyManager = new EnemyManager(scene);
const hud = new HUD();

const clock = new THREE.Clock();
let waveTimer = 0;
let nextWave = 1;
let betweenWaves = false;
let ammoLowPlayed = false;

// Pointer lock events
player.controls.addEventListener('lock', () => {
  if (state === MENU || state === GAME_OVER) {
    state = PLAYING;
    hud.show();
    audio.init();
    audio.startAmbientDrone();
    if (state === GAME_OVER || nextWave > 1) {
      enemyManager.reset();
      player.respawn();
      nextWave = 1;
      betweenWaves = false;
      hud.updateScore(0);
    }
    startWave(nextWave);
  }
});

player.controls.addEventListener('unlock', () => {
  if (state === PLAYING) {
    hud.hide();
  }
});

// Overlay click
document.getElementById('blocker').addEventListener('click', () => {
  player.lock();
});

function startWave(wave) {
  enemyManager.startWave(wave, audio, particles);
  hud.updateWave(wave);
  hud.showWaveAnnouncement(wave);
  betweenWaves = false;
}

// Key bindings
document.addEventListener('keydown', (e) => {
  if (state !== PLAYING) return;
  if (e.code === 'Digit1') player.switchWeapon(0);
  if (e.code === 'Digit2') player.switchWeapon(1);
  if (e.code === 'Digit3') player.switchWeapon(2);
  if (e.code === 'KeyR') player.startReload();
});

// Game loop
function animate() {
  requestAnimationFrame(animate);

  const delta = Math.min(clock.getDelta(), 0.1);

  if (state === PLAYING) {
    // Player update
    player.update(delta, null, colliders, audio);

    // Audio listener sync
    audio.updateListener(player.camera.position);

    // Weapon switch via keys
    if (isKeyDown('Digit1')) player.switchWeapon(0);
    if (isKeyDown('Digit2')) player.switchWeapon(1);
    if (isKeyDown('Digit3')) player.switchWeapon(2);

    // Weapon switch via mouse wheel
    if (inputState.wheelDelta) {
      const dir = inputState.wheelDelta > 0 ? 1 : -1;
      const next = (player.currentWeapon + dir + WEAPONS.length) % WEAPONS.length;
      player.switchWeapon(next);
      inputState.wheelDelta = 0;
      ammoLowPlayed = false;
    }

    // Shooting
    if (inputState.mouseDown) {
      const aliveEnemies = enemyManager.getAliveEnemies();
      const hit = player.shoot(aliveEnemies, particles, audio);
      if (hit) {
        hud.showHitMarker();
      }
    }

    // Enemies
    const playerAttacked = enemyManager.update(delta, player.position, particles, audio, colliders);
    if (playerAttacked) {
      player.takeDamage(CONFIG.ENEMY_DAMAGE, audio);
      hud.showDamage();
    }

    // Wave management
    if (enemyManager.allDead() && !betweenWaves) {
      betweenWaves = true;
      waveTimer = CONFIG.WAVE_BREAK_DURATION;
    }

    if (betweenWaves) {
      waveTimer -= delta;
      if (waveTimer <= 0) {
        nextWave = enemyManager.wave + 1;
        startWave(nextWave);
      }
    }

    // Player death
    if (!player.alive) {
      state = GAME_OVER;
      hud.showGameOver(enemyManager.score);
      player.controls.unlock();
      audio.stopAmbientDrone();
    }

    // HUD updates
    const weapon = WEAPONS[player.currentWeapon];
    hud.updateHealth(player.health, player.maxHealth);
    hud.updateWeapon(weapon.name, player.ammo[player.currentWeapon], weapon.ammoMax);
    hud.updateScore(enemyManager.score);

    // Low ammo warning
    if (player.ammo[player.currentWeapon] <= 5 && player.ammo[player.currentWeapon] > 0 && !ammoLowPlayed) {
      audio.playAmmoLow();
      ammoLowPlayed = true;
    }
    if (player.ammo[player.currentWeapon] > 5) {
      ammoLowPlayed = false;
    }
  }

  // Always update
  particles.update(delta);
  updateBeamPool(delta);
  updateSpread(delta);

  // Floating decorations
  const t = performance.now() * 0.001;
  decos.forEach((d, i) => {
    d.rotation.x = t * 0.5 + i;
    d.rotation.y = t * 0.3 + i * 2;
    d.position.y = 3 + Math.sin(t + i) * 0.5;
  });

  composer.render();
}

animate();

// Resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  composer.setSize(window.innerWidth, window.innerHeight);
  bloomPass.resolution.set(window.innerWidth, window.innerHeight);
});
