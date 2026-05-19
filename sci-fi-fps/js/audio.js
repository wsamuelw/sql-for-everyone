import { CONFIG } from './config.js';

export class AudioManager {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.convolver = null;
    this.reverbGain = null;
    this.droneOsc = null;
    this.droneLFO = null;
  }

  init() {
    if (this.ctx) return;
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.3;
    this.masterGain.connect(this.ctx.destination);

    // Reverb
    this.convolver = this.ctx.createConvolver();
    this.convolver.buffer = this._createImpulseResponse(CONFIG.REVERB_DECAY, CONFIG.REVERB_DECAY);
    this.reverbGain = this.ctx.createGain();
    this.reverbGain.gain.value = 0.3;
    this.convolver.connect(this.reverbGain);
    this.reverbGain.connect(this.masterGain);
  }

  _createImpulseResponse(duration, decay) {
    const length = this.ctx.sampleRate * duration;
    const buffer = this.ctx.createBuffer(2, length, this.ctx.sampleRate);
    for (let ch = 0; ch < 2; ch++) {
      const data = buffer.getChannelData(ch);
      for (let i = 0; i < length; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
      }
    }
    return buffer;
  }

  _createPanner(position) {
    if (!this.ctx) return this.masterGain;
    const panner = this.ctx.createPanner();
    panner.panningModel = 'HRTF';
    panner.distanceModel = 'inverse';
    panner.refDistance = CONFIG.SPATIAL_AUDIO_REF_DISTANCE;
    panner.maxDistance = CONFIG.SPATIAL_AUDIO_MAX_DISTANCE;
    panner.positionX.setValueAtTime(position.x, this.ctx.currentTime);
    panner.positionY.setValueAtTime(position.y, this.ctx.currentTime);
    panner.positionZ.setValueAtTime(position.z, this.ctx.currentTime);
    panner.connect(this.masterGain);
    panner.connect(this.convolver);
    return panner;
  }

  updateListener(cameraPosition) {
    if (!this.ctx) return;
    this.ctx.listener.positionX.setValueAtTime(cameraPosition.x, this.ctx.currentTime);
    this.ctx.listener.positionY.setValueAtTime(cameraPosition.y, this.ctx.currentTime);
    this.ctx.listener.positionZ.setValueAtTime(cameraPosition.z, this.ctx.currentTime);
  }

  _noise(duration, frequency, type = 'sawtooth', target = null) {
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(frequency, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(frequency * 0.25, this.ctx.currentTime + duration);
    gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(target || this.masterGain);
    gain.connect(this.convolver);
    osc.start();
    osc.stop(this.ctx.currentTime + duration);
  }

  playShot(weaponType, position) {
    if (!this.ctx) return;
    const target = position ? this._createPanner(position) : this.masterGain;

    if (weaponType === 0) {
      // Plasma Rifle — crackle burst
      const osc1 = this.ctx.createOscillator();
      const osc2 = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc1.type = 'sawtooth';
      osc1.frequency.setValueAtTime(300, this.ctx.currentTime);
      osc1.frequency.exponentialRampToValueAtTime(50, this.ctx.currentTime + 0.08);
      osc2.type = 'sawtooth';
      osc2.frequency.setValueAtTime(900, this.ctx.currentTime);
      osc2.frequency.exponentialRampToValueAtTime(100, this.ctx.currentTime + 0.06);
      gain.gain.setValueAtTime(0.25, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);
      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(target);
      gain.connect(this.convolver);
      osc1.start();
      osc2.start();
      osc1.stop(this.ctx.currentTime + 0.08);
      osc2.stop(this.ctx.currentTime + 0.08);
    } else if (weaponType === 1) {
      // Laser Cannon — sustained hum + zap
      const osc = this.ctx.createOscillator();
      const zap = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(200, this.ctx.currentTime + 0.15);
      zap.type = 'square';
      zap.frequency.setValueAtTime(1600, this.ctx.currentTime);
      zap.frequency.exponentialRampToValueAtTime(400, this.ctx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);
      osc.connect(gain);
      zap.connect(gain);
      gain.connect(target);
      gain.connect(this.convolver);
      osc.start();
      zap.start();
      osc.stop(this.ctx.currentTime + 0.15);
      zap.stop(this.ctx.currentTime + 0.15);
    } else {
      // Spread Gun — multi-pop
      for (let i = 0; i < 3; i++) {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(400 + i * 100, this.ctx.currentTime + i * 0.01);
        osc.frequency.exponentialRampToValueAtTime(80, this.ctx.currentTime + i * 0.01 + 0.05);
        gain.gain.setValueAtTime(0.2, this.ctx.currentTime + i * 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + i * 0.01 + 0.05);
        osc.connect(gain);
        gain.connect(target);
        gain.connect(this.convolver);
        osc.start(this.ctx.currentTime + i * 0.01);
        osc.stop(this.ctx.currentTime + i * 0.01 + 0.05);
      }
    }
  }

  playHit(target = null) {
    if (!this.ctx) return;
    const dest = target || this.masterGain;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'square';
    osc.frequency.value = 600;
    gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.03);
    osc.connect(gain);
    gain.connect(dest);
    gain.connect(this.convolver);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.03);
  }

  playExplosion(target = null) {
    if (!this.ctx) return;
    const dest = target || this.masterGain;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(60, this.ctx.currentTime);
    gain.gain.setValueAtTime(0.4, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.3);
    osc.connect(gain);
    gain.connect(dest);
    gain.connect(this.convolver);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.3);
    this._noise(0.2, 100, 'sawtooth', dest);
  }

  playDamage() {
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(300, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(100, this.ctx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.1);
    osc.connect(gain);
    gain.connect(this.masterGain);
    gain.connect(this.convolver);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.1);
  }

  playWaveStart() {
    if (!this.ctx) return;
    [400, 500, 600].forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.15, this.ctx.currentTime + i * 0.12);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + i * 0.12 + 0.1);
      osc.connect(gain);
      gain.connect(this.masterGain);
      gain.connect(this.convolver);
      osc.start(this.ctx.currentTime + i * 0.12);
      osc.stop(this.ctx.currentTime + i * 0.12 + 0.1);
    });
  }

  playAmmoLow() {
    if (!this.ctx) return;
    [800, 600].forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'square';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.1, this.ctx.currentTime + i * 0.15);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + i * 0.15 + 0.08);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(this.ctx.currentTime + i * 0.15);
      osc.stop(this.ctx.currentTime + i * 0.15 + 0.08);
    });
  }

  playEnemyGrowl(position) {
    if (!this.ctx) return;
    const target = this._createPanner(position);
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(80, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, this.ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);
    osc.connect(gain);
    gain.connect(target);
    gain.connect(this.convolver);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.15);
  }

  playEnemyScreech(position) {
    if (!this.ctx) return;
    const target = this._createPanner(position);
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(1200, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(400, this.ctx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.1);
    osc.connect(gain);
    gain.connect(target);
    gain.connect(this.convolver);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.1);
  }

  playEnemyDeathScream(position) {
    if (!this.ctx) return;
    const target = this._createPanner(position);
    // Low rumble
    const osc1 = this.ctx.createOscillator();
    const gain1 = this.ctx.createGain();
    osc1.type = 'sawtooth';
    osc1.frequency.setValueAtTime(80, this.ctx.currentTime);
    osc1.frequency.exponentialRampToValueAtTime(20, this.ctx.currentTime + 0.4);
    gain1.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain1.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.4);
    osc1.connect(gain1);
    gain1.connect(target);
    gain1.connect(this.convolver);
    osc1.start();
    osc1.stop(this.ctx.currentTime + 0.4);
    // High screech
    const osc2 = this.ctx.createOscillator();
    const gain2 = this.ctx.createGain();
    osc2.type = 'square';
    osc2.frequency.setValueAtTime(1400, this.ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(200, this.ctx.currentTime + 0.3);
    gain2.gain.setValueAtTime(0.15, this.ctx.currentTime);
    gain2.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.3);
    osc2.connect(gain2);
    gain2.connect(target);
    gain2.connect(this.convolver);
    osc2.start();
    osc2.stop(this.ctx.currentTime + 0.3);
  }

  startAmbientDrone() {
    if (!this.ctx || this.droneOsc) return;
    this.droneOsc = this.ctx.createOscillator();
    this.droneGain = this.ctx.createGain();
    this.droneOsc.type = 'sine';
    this.droneOsc.frequency.value = CONFIG.AMBIENT_DRONE_FREQ;
    this.droneGain.gain.value = CONFIG.AMBIENT_DRONE_GAIN;
    this.droneLFO = this.ctx.createOscillator();
    this.droneLFOGain = this.ctx.createGain();
    this.droneLFO.frequency.value = 0.3;
    this.droneLFOGain.gain.value = 0.01;
    this.droneLFO.connect(this.droneLFOGain);
    this.droneLFOGain.connect(this.droneGain.gain);
    this.droneOsc.connect(this.droneGain);
    this.droneGain.connect(this.masterGain);
    this.droneOsc.start();
    this.droneLFO.start();
  }

  stopAmbientDrone() {
    if (this.droneOsc) { this.droneOsc.stop(); this.droneOsc = null; }
    if (this.droneLFO) { this.droneLFO.stop(); this.droneLFO = null; }
  }

  playFootstep() {
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(200, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(50, this.ctx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.04);
    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.04);
  }
}
