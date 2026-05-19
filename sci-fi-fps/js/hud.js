export class HUD {
  constructor() {
    this.healthFill = document.getElementById('health-bar-fill');
    this.healthText = document.getElementById('health-text');
    this.weaponName = document.getElementById('weapon-name');
    this.ammoCurrent = document.getElementById('ammo-current');
    this.ammoMax = document.getElementById('ammo-max');
    this.scoreEl = document.getElementById('score');
    this.waveEl = document.getElementById('wave');
    this.damageVignette = document.getElementById('damage-vignette');
    this.waveAnnounce = document.getElementById('wave-announce');
    this.hudEl = document.getElementById('hud');
    this.blocker = document.getElementById('blocker');
    this.instructions = document.getElementById('instructions');
    this.gameOver = document.getElementById('game-over');
    this.finalScore = document.getElementById('final-score');
    this.hitMarker = document.getElementById('hit-marker');
  }

  show() {
    this.hudEl.classList.remove('hidden');
    this.blocker.classList.add('hidden');
  }

  hide() {
    this.hudEl.classList.add('hidden');
    this.blocker.classList.remove('hidden');
  }

  showMenu() {
    this.instructions.classList.remove('hidden');
    this.gameOver.classList.add('hidden');
    this.blocker.classList.remove('hidden');
  }

  showGameOver(score) {
    this.instructions.classList.add('hidden');
    this.gameOver.classList.remove('hidden');
    this.finalScore.textContent = `Score: ${score}`;
    this.blocker.classList.remove('hidden');
  }

  updateHealth(current, max) {
    const pct = Math.max(0, current / max * 100);
    this.healthFill.style.width = `${pct}%`;
    this.healthText.textContent = Math.ceil(current);

    if (pct > 50) {
      this.healthFill.style.background = 'linear-gradient(90deg, #0f0, #0f0)';
      this.healthFill.style.boxShadow = '0 0 8px #0f0';
    } else if (pct > 25) {
      this.healthFill.style.background = 'linear-gradient(90deg, #ff0, #ff0)';
      this.healthFill.style.boxShadow = '0 0 8px #ff0';
    } else {
      this.healthFill.style.background = 'linear-gradient(90deg, #f00, #f00)';
      this.healthFill.style.boxShadow = '0 0 8px #f00';
    }
  }

  updateAmmo(current, max) {
    this.ammoCurrent.textContent = current;
    this.ammoMax.textContent = max;
    if (current <= 5) {
      this.ammoCurrent.classList.add('low');
    } else {
      this.ammoCurrent.classList.remove('low');
    }
  }

  updateWeapon(name, ammo, max) {
    this.weaponName.textContent = name;
    this.updateAmmo(ammo, max);
  }

  updateScore(score) {
    this.scoreEl.textContent = score;
  }

  updateWave(wave) {
    this.waveEl.textContent = wave;
  }

  showDamage() {
    this.damageVignette.classList.add('flash');
    setTimeout(() => this.damageVignette.classList.remove('flash'), 150);
  }

  showWaveAnnouncement(wave) {
    this.waveAnnounce.textContent = `WAVE ${wave}`;
    this.waveAnnounce.classList.remove('hidden');
    this.waveAnnounce.classList.add('visible');
    setTimeout(() => {
      this.waveAnnounce.classList.remove('visible');
      setTimeout(() => this.waveAnnounce.classList.add('hidden'), 500);
    }, 2000);
  }

  showHitMarker() {
    if (!this.hitMarker) return;
    this.hitMarker.classList.add('active');
    setTimeout(() => this.hitMarker.classList.remove('active'), 100);
  }
}
