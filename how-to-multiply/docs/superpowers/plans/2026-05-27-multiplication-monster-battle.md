# How to Multiply — Monster Battle Arena Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file HTML multiplication game where kids battle monsters by answering math questions correctly.

**Architecture:** Single `index.html` file containing all HTML, CSS, and JavaScript. Game state managed in a central `state` object, persisted to localStorage. Screen routing via a simple `showScreen()` function that toggles div visibility. All game logic in plain JS — no frameworks, no build tools.

**Tech Stack:** Vanilla HTML/CSS/JS, localStorage for persistence, CSS animations for effects.

---

## File Structure

| File | Responsibility |
|------|---------------|
| `index.html` | Single file: all markup, styles, and game logic |

---

### Task 1: Project skeleton + CSS foundation

**Files:**
- Create: `index.html`

- [ ] **Step 1: Create index.html with HTML structure and CSS reset**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>How to Multiply — Monster Battle Arena</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif;
      background: #1a1a2e;
      color: #fff;
      min-height: 100vh;
      min-height: 100dvh;
      overflow: hidden;
      user-select: none;
      -webkit-user-select: none;
    }
    .screen { display: none; width: 100%; height: 100vh; height: 100dvh; position: absolute; top: 0; left: 0; }
    .screen.active { display: flex; flex-direction: column; }

    /* Title Screen */
    #title-screen {
      align-items: center;
      justify-content: center;
      background: linear-gradient(180deg, #FF6B6B 0%, #FFE66D 100%);
      gap: 24px;
    }
    #title-screen h1 {
      font-size: 42px;
      text-shadow: 3px 3px 0 #333;
      text-align: center;
    }
    #title-screen .subtitle {
      font-size: 18px;
      opacity: 0.8;
    }
    .title-monster {
      font-size: 100px;
      animation: bounce 1s ease-in-out infinite;
    }
    @keyframes bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-20px); }
    }
    .btn {
      display: inline-block;
      padding: 16px 48px;
      border: none;
      border-radius: 16px;
      font-size: 22px;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 0 4px 0 rgba(0,0,0,0.3);
      transition: transform 0.1s, box-shadow 0.1s;
      min-width: 200px;
    }
    .btn:active {
      transform: translateY(4px);
      box-shadow: 0 0 0 rgba(0,0,0,0.3);
    }
    .btn-primary { background: #4CAF50; color: #fff; }
    .btn-secondary { background: #fff; color: #333; }
    .btn-back {
      position: absolute;
      top: 16px;
      left: 16px;
      padding: 8px 16px;
      font-size: 16px;
      min-width: auto;
      background: rgba(0,0,0,0.3);
      color: #fff;
      border-radius: 12px;
    }
  </style>
</head>
<body>
  <!-- Title Screen -->
  <div id="title-screen" class="screen active">
    <div class="title-monster">&#128126;</div>
    <h1>How to Multiply</h1>
    <p class="subtitle">Monster Battle Arena</p>
    <button class="btn btn-primary" onclick="startBattle()">Battle!</button>
    <button class="btn btn-secondary" onclick="showScreen('collection-screen')">Collection</button>
  </div>

  <!-- Battle Screen -->
  <div id="battle-screen" class="screen"></div>

  <!-- Collection Screen -->
  <div id="collection-screen" class="screen"></div>

  <!-- Times Table Screen -->
  <div id="table-screen" class="screen"></div>

  <script>
    // Game state
    const state = {
      level: 1,
      coins: 0,
      selectedTable: 1,
      selectedMonster: 0,
      monsters: [
        { id: 0, name: 'Flamey', emoji: '\u{1F525}', type: 'Fire', hp: 10, attack: 2, battles: 0, evolved: false }
      ],
      unlockedMonsters: [0],
      streak: 0
    };

    function showScreen(id) {
      document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
      document.getElementById(id).classList.add('active');
    }

    function startBattle() {
      showScreen('battle-screen');
    }
  </script>
</body>
</html>
```

- [ ] **Step 2: Open in browser and verify title screen renders**

Open `index.html` in browser. Expected: gradient background, bouncing monster emoji, "How to Multiply" title, "Battle!" and "Collection" buttons. Tap buttons to verify screen switching works.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add project skeleton with title screen"
```

---

### Task 2: Game data + question generation

**Files:**
- Modify: `index.html` (add to `<script>` block)

- [ ] **Step 1: Add monster definitions, enemy names, and question generator**

Add this inside the `<script>` tag, after the existing `state` object:

```javascript
// Monster definitions
const MONSTERS = [
  { id: 0, name: 'Flamey', emoji: '\u{1F525}', type: 'Fire', hp: 10, attack: 2, evolveName: 'Mega Flamey', evolveEmoji: '\u{1F30B}' },
  { id: 1, name: 'Rocky', emoji: '\u{1FAA8}', type: 'Earth', hp: 12, attack: 2, unlockLevel: 5, evolveName: 'Titan Rocky', evolveEmoji: '\u{26F0}️' },
  { id: 2, name: 'Sparky', emoji: '\u{26A1}', type: 'Electric', hp: 8, attack: 4, unlockLevel: 10, evolveName: 'Mega Sparky', evolveEmoji: '\u{26A1}' },
  { id: 3, name: 'Frosty', emoji: '\u{2744}️', type: 'Ice', hp: 14, attack: 3, unlockLevel: 15, evolveName: 'Blizzard', evolveEmoji: '\u{1F328}️' },
  { id: 4, name: 'Shadow', emoji: '\u{1F47B}', type: 'Dark', hp: 10, attack: 5, unlockLevel: 20, evolveName: 'Nightmare', evolveEmoji: '\u{1F47B}' }
];

// Enemy names for random generation
const ENEMY_NAMES = [
  'Grumble', 'Snarl', 'Nip', 'Chomp', 'Gnash',
  'Bitey', 'Scratch', 'Rumble', 'Growl', 'Snap',
  'Pinch', 'Stinger', 'Claw', 'Fang', 'Thorn'
];
const ENEMY_EMOJIS = ['\u{1F47E}', '\u{1F984}', '\u{1F40D}', '\u{1F419}', '\u{1F98A}', '\u{1F43B}', '\u{1F432}'];

// Times table unlock order
const TABLE_UNLOCK_LEVELS = {
  1: 0, 2: 5, 5: 10, 10: 15, 3: 20, 4: 25,
  6: 30, 7: 35, 8: 40, 9: 45, 11: 50, 12: 55
};
const TABLE_ORDER = [1, 2, 5, 10, 3, 4, 6, 7, 8, 9, 11, 12];

// Encouraging messages
const WIN_MESSAGES = ['Awesome!', 'Great job!', 'You rock!', 'Nailed it!', 'Super star!'];
const LOSE_MESSAGES = ["Almost! Try again!", "You'll get it!", "So close!", "Keep trying!"];
const CORRECT_MESSAGES = ['\u{1F44D}', '\u{2B50}', '\u{1F389}', '\u{1F44E}'];

function generateQuestion(table) {
  const a = Math.floor(Math.random() * 12) + 1;
  const correct = table * a;
  const wrongs = new Set();
  while (wrongs.size < 2) {
    const offset = Math.floor(Math.random() * 9) - 4;
    const wrong = correct + offset;
    if (wrong !== correct && wrong > 0 && !wrongs.has(wrong)) {
      wrongs.add(wrong);
    }
  }
  const options = [correct, ...wrongs];
  // Shuffle
  for (let i = options.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [options[i], options[j]] = [options[j], options[i]];
  }
  return { a, table, correct, options };
}

function getEnemy(level) {
  const isBoss = level % 5 === 0;
  const name = ENEMY_NAMES[Math.floor(Math.random() * ENEMY_NAMES.length)];
  const emoji = isBoss ? '\u{1F47E}' : ENEMY_EMOJIS[Math.floor(Math.random() * ENEMY_EMOJIS.length)];
  const hp = Math.floor(8 + level * 1.5) * (isBoss ? 2 : 1);
  const attack = Math.floor(1 + level * 0.3) * (isBoss ? 1.5 : 1);
  return { name, emoji, hp, maxHp: hp, attack, isBoss };
}
```

- [ ] **Step 2: Open browser console, test generateQuestion and getEnemy**

Run in console:
```javascript
generateQuestion(6)  // Should return {a: number, table: 6, correct: number, options: [3 numbers]}
getEnemy(1)          // Should return {name, emoji, hp: ~9, maxHp: ~9, attack: ~1, isBoss: false}
getEnemy(5)          // Should return boss with hp ~15 * 2 = 30, isBoss: true
```

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add game data, question generation, and enemy scaling"
```

---

### Task 3: Battle screen layout + HP bars

**Files:**
- Modify: `index.html` (replace battle-screen div content, add CSS)

- [ ] **Step 1: Add battle screen CSS**

Add to the `<style>` block:

```css
/* Battle Screen */
#battle-screen {
  background: linear-gradient(180deg, #87CEEB 0%, #87CEEB 60%, #90EE90 60%, #228B22 100%);
}
.battle-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: rgba(0,0,0,0.3);
  font-size: 14px;
  font-weight: bold;
}
.battle-topbar .coins { color: #FFD700; }
.battle-area {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}
.monster-slot {
  text-align: center;
  position: relative;
}
.monster-emoji {
  font-size: 72px;
  transition: transform 0.3s;
}
.monster-emoji.boss { font-size: 96px; }
.monster-name {
  background: rgba(0,0,0,0.5);
  color: #fff;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  margin-top: 4px;
}
.hp-bar {
  width: 80px;
  height: 10px;
  background: #333;
  border-radius: 5px;
  margin: 6px auto 0;
  overflow: hidden;
}
.hp-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.4s ease;
}
.hp-fill.player { background: linear-gradient(90deg, #4CAF50, #8BC34A); }
.hp-fill.enemy { background: linear-gradient(90deg, #f44336, #FF9800); }
.vs-text {
  font-size: 32px;
  font-weight: bold;
  text-shadow: 2px 2px 0 #333;
  color: #FFD700;
}
.boss-border {
  border: 3px solid #FFD700;
  border-radius: 50%;
  padding: 4px;
  animation: bossPulse 1.5s ease-in-out infinite;
}
@keyframes bossPulse {
  0%, 100% { box-shadow: 0 0 10px #FFD700; }
  50% { box-shadow: 0 0 25px #FFD700; }
}

/* Question Panel */
.question-panel {
  background: rgba(255,255,255,0.95);
  border-radius: 20px 20px 0 0;
  padding: 20px;
  text-align: center;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
}
.question-text {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
}
.answer-options {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.answer-btn {
  background: #4CAF50;
  color: #fff;
  border: none;
  padding: 14px 32px;
  border-radius: 14px;
  font-size: 22px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 0 #388E3C;
  transition: transform 0.1s, box-shadow 0.1s;
  min-width: 80px;
}
.answer-btn:active {
  transform: translateY(4px);
  box-shadow: 0 0 0 #388E3C;
}
.answer-btn.correct {
  background: #4CAF50 !important;
  animation: correctPop 0.3s ease;
}
.answer-btn.wrong {
  background: #f44336 !important;
  animation: wrongShake 0.4s ease;
}
@keyframes correctPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
}
@keyframes wrongShake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-8px); }
  40% { transform: translateX(8px); }
  60% { transform: translateX(-6px); }
  80% { transform: translateX(6px); }
}
@keyframes attackRight {
  0% { transform: translateX(0); }
  40% { transform: translateX(40px); }
  100% { transform: translateX(0); }
}
@keyframes attackLeft {
  0% { transform: translateX(0); }
  40% { transform: translateX(-40px); }
  100% { transform: translateX(0); }
}
@keyframes shakeHit {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px) rotate(-3deg); }
  75% { transform: translateX(5px) rotate(3deg); }
}
```

- [ ] **Step 2: Build the renderBattle function**

Add to `<script>`:

```javascript
let currentEnemy = null;
let currentQuestion = null;
let playerHp = 0;
let playerMaxHp = 0;

function renderBattle() {
  const monster = getActiveMonster();
  currentEnemy = getEnemy(state.level);
  playerHp = monster.hp;
  playerMaxHp = monster.hp;

  const isBoss = currentEnemy.isBoss;
  document.getElementById('battle-screen').innerHTML = `
    <div class="battle-topbar">
      <span>Level ${state.level}${isBoss ? ' BOSS' : ''}</span>
      <span class="coins">\u{1FA99} ${state.coins}</span>
      <span>x${state.selectedTable} Table</span>
    </div>
    <div class="battle-area">
      <div class="monster-slot" id="player-slot">
        <div class="${isBoss ? '' : ''}">
          <span class="monster-emoji player-monster ${isBoss ? '' : ''}" style="font-size:64px">${monster.emoji}</span>
        </div>
        <div class="monster-name" style="background:#333;color:#4CAF50;padding:2px 10px;border-radius:10px;font-size:12px;margin-top:4px">${monster.name}</div>
        <div class="hp-bar"><div class="hp-fill player" id="player-hp" style="width:100%"></div></div>
      </div>
      <div class="vs-text">VS</div>
      <div class="monster-slot" id="enemy-slot">
        <div class="${isBoss ? 'boss-border' : ''}">
          <span class="monster-emoji enemy-monster" style="font-size:${isBoss ? '80px' : '64px'}">${currentEnemy.emoji}</span>
        </div>
        <div class="monster-name" style="background:#333;color:#9C27B0;padding:2px 10px;border-radius:10px;font-size:12px;margin-top:4px">${currentEnemy.name}${isBoss ? ' BOSS' : ''}</div>
        <div class="hp-bar"><div class="hp-fill enemy" id="enemy-hp" style="width:100%"></div></div>
      </div>
    </div>
    <div class="question-panel">
      <div class="question-text" id="question-text"></div>
      <div class="answer-options" id="answer-options"></div>
    </div>
  `;
  nextQuestion();
}

function getActiveMonster() {
  const def = MONSTERS[state.selectedMonster];
  const owned = state.monsters.find(m => m.id === state.selectedMonster);
  const hp = owned && owned.evolved ? Math.floor(def.hp * 1.5) : def.hp;
  const atk = owned && owned.evolved ? Math.floor(def.attack * 1.5) : def.attack;
  const emoji = owned && owned.evolved ? def.evolveEmoji : def.emoji;
  const name = owned && owned.evolved ? def.evolveName : def.name;
  return { ...def, hp, attack: atk, emoji, name };
}

function nextQuestion() {
  currentQuestion = generateQuestion(state.selectedTable);
  document.getElementById('question-text').textContent =
    `${currentQuestion.table} x ${currentQuestion.a} = ?`;
  const container = document.getElementById('answer-options');
  container.innerHTML = currentQuestion.options.map(opt =>
    `<button class="answer-btn" onclick="submitAnswer(${opt})">${opt}</button>`
  ).join('');
}

function submitAnswer(choice) {
  const btns = document.querySelectorAll('.answer-btn');
  btns.forEach(b => b.disabled = true);

  const isCorrect = choice === currentQuestion.correct;
  const playerMonster = document.getElementById('player-slot');
  const enemyMonster = document.getElementById('enemy-slot');

  if (isCorrect) {
    state.streak++;
    const dmg = getActiveMonster().attack;
    currentEnemy.hp -= dmg;
    // Animate player attack
    playerMonster.style.animation = 'attackRight 0.3s ease';
    setTimeout(() => { playerMonster.style.animation = ''; }, 300);
    // Show damage
    showDamageText(enemyMonster, `-${dmg}`, '#FF6B6B');

    // Update enemy HP
    const pct = Math.max(0, currentEnemy.hp / currentEnemy.maxHp * 100);
    document.getElementById('enemy-hp').style.width = pct + '%';

    // Highlight correct
    btns.forEach(b => {
      if (parseInt(b.textContent) === currentQuestion.correct) b.classList.add('correct');
    });

    if (currentEnemy.hp <= 0) {
      setTimeout(() => winBattle(), 600);
    } else {
      setTimeout(() => nextQuestion(), 800);
    }
  } else {
    state.streak = 0;
    const dmg = Math.floor(currentEnemy.attack);
    playerHp -= dmg;
    // Animate enemy attack
    enemyMonster.style.animation = 'attackLeft 0.3s ease';
    setTimeout(() => { enemyMonster.style.animation = ''; }, 300);
    showDamageText(playerMonster, `-${dmg}`, '#f44336');

    // Update player HP
    const pct = Math.max(0, playerHp / playerMaxHp * 100);
    document.getElementById('player-hp').style.width = pct + '%';

    // Highlight wrong
    btns.forEach(b => {
      if (parseInt(b.textContent) === choice) b.classList.add('wrong');
      if (parseInt(b.textContent) === currentQuestion.correct) b.classList.add('correct');
    });

    if (playerHp <= 0) {
      setTimeout(() => loseBattle(), 600);
    } else {
      setTimeout(() => nextQuestion(), 800);
    }
  }
}

function showDamageText(parent, text, color) {
  const el = document.createElement('div');
  el.textContent = text;
  el.style.cssText = `position:absolute;font-size:28px;font-weight:bold;color:${color};text-shadow:1px 1px 0 #000;pointer-events:none;animation:floatUp 0.8s ease forwards;z-index:10;`;
  parent.style.position = 'relative';
  parent.appendChild(el);
  setTimeout(() => el.remove(), 800);
}

function winBattle() {
  const coinsEarned = currentEnemy.isBoss ? 25 : 10;
  const streakBonus = state.streak >= 3 ? (state.streak - 2) * 5 : 0;
  state.coins += coinsEarned + streakBonus;

  // Check monster unlocks
  if (currentEnemy.isBoss) {
    const unlockable = MONSTERS.find(m => m.unlockLevel === state.level && !state.unlockedMonsters.includes(m.id));
    if (unlockable) {
      state.unlockedMonsters.push(unlockable.id);
      state.monsters.push({ id: unlockable.id, name: unlockable.name, battles: 0, evolved: false });
    }
  }

  // Track battles for active monster
  const owned = state.monsters.find(m => m.id === state.selectedMonster);
  if (owned) {
    owned.battles++;
    if (owned.battles >= 20 && !owned.evolved) {
      owned.evolved = true;
    }
  }

  state.level++;
  saveState();

  const msg = WIN_MESSAGES[Math.floor(Math.random() * WIN_MESSAGES.length)];
  document.getElementById('battle-screen').innerHTML = `
    <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;background:linear-gradient(180deg,#4CAF50,#2E7D32);">
      <div style="font-size:64px;">\u{1F3C6}</div>
      <div style="font-size:36px;font-weight:bold;">YOU WIN!</div>
      <div style="font-size:22px;">${msg}</div>
      <div style="font-size:18px;color:#FFD700;">\u{1FA99} +${coinsEarned}${streakBonus > 0 ? ` (+${streakBonus} streak!)` : ''}</div>
      <button class="btn btn-primary" onclick="renderBattle()" style="margin-top:20px">Next Battle</button>
    </div>
  `;
}

function loseBattle() {
  const msg = LOSE_MESSAGES[Math.floor(Math.random() * LOSE_MESSAGES.length)];
  document.getElementById('battle-screen').innerHTML = `
    <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;background:linear-gradient(180deg,#f44336,#c62828);">
      <div style="font-size:64px;">\u{1F622}</div>
      <div style="font-size:36px;font-weight:bold;">OH NO!</div>
      <div style="font-size:22px;">${msg}</div>
      <button class="btn btn-primary" onclick="renderBattle()" style="margin-top:20px">Try Again</button>
      <button class="btn btn-secondary" onclick="showScreen('title-screen')" style="margin-top:8px">Home</button>
    </div>
  `;
}
```

- [ ] **Step 3: Add floatUp animation to CSS**

Add to `<style>`:

```css
@keyframes floatUp {
  0% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-40px); }
}
```

- [ ] **Step 4: Wire up the startBattle function**

Update the existing `startBattle` function:

```javascript
function startBattle() {
  renderBattle();
  showScreen('battle-screen');
}
```

- [ ] **Step 5: Open browser, play through a full battle**

Click "Battle!", answer questions. Verify:
- Question appears with 3 options
- Correct answer: green flash, enemy HP drops, attack animation
- Wrong answer: red flash, player HP drops, shake animation
- Win: victory screen with coins
- Lose: retry screen

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: add battle screen with HP bars, attacks, and question flow"
```

---

### Task 4: localStorage persistence

**Files:**
- Modify: `index.html` (add to `<script>`)

- [ ] **Step 1: Add save/load functions**

```javascript
const SAVE_KEY = 'how-to-multiply-save';

function saveState() {
  localStorage.setItem(SAVE_KEY, JSON.stringify({
    level: state.level,
    coins: state.coins,
    selectedTable: state.selectedTable,
    selectedMonster: state.selectedMonster,
    monsters: state.monsters,
    unlockedMonsters: state.unlockedMonsters,
    streak: state.streak
  }));
}

function loadState() {
  const raw = localStorage.getItem(SAVE_KEY);
  if (raw) {
    try {
      const data = JSON.parse(raw);
      Object.assign(state, data);
    } catch(e) { /* fresh state */ }
  }
}

// Load on startup
loadState();
```

- [ ] **Step 2: Add saveState() call after battle outcomes**

Already done in `winBattle()` from Task 3. Add to `loseBattle()` too — update the function to also call `saveState()` (state doesn't change on loss, but good to have the hook).

- [ ] **Step 3: Test persistence — win a battle, refresh page, check coins and level persist**

Open browser, win a battle, note coins/level, refresh page, verify values are preserved.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add localStorage persistence for game progress"
```

---

### Task 5: Monster collection screen

**Files:**
- Modify: `index.html` (add collection screen CSS + render function)

- [ ] **Step 1: Add collection screen CSS**

```css
/* Collection Screen */
#collection-screen {
  background: linear-gradient(180deg, #1a1a4e 0%, #2d1b69 100%);
  padding: 16px;
}
.collection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.collection-header h2 { font-size: 22px; }
.monster-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.monster-card {
  background: rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 12px;
  text-align: center;
  border: 2px solid transparent;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.1s;
}
.monster-card.owned { border-color: #4CAF50; }
.monster-card.selected { border-color: #FFD700; background: rgba(255,215,0,0.15); }
.monster-card.locked { opacity: 0.4; border: 2px dashed #555; cursor: default; }
.monster-card .m-emoji { font-size: 40px; }
.monster-card .m-name { color: #fff; font-size: 12px; margin-top: 4px; }
.monster-card .m-level { font-size: 10px; margin-top: 2px; }
.monster-card .m-locked-text { color: #f44336; font-size: 10px; margin-top: 4px; }
.evolution-panel {
  background: rgba(255,255,255,0.1);
  border-radius: 14px;
  padding: 14px;
}
.evolution-panel h3 { font-size: 14px; margin-bottom: 8px; }
.evolution-bar {
  width: 100%;
  height: 10px;
  background: #333;
  border-radius: 5px;
  overflow: hidden;
}
.evolution-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B6B, #FFD700);
  border-radius: 5px;
  transition: width 0.4s;
}
.evolution-label { font-size: 11px; color: #888; margin-top: 4px; }
```

- [ ] **Step 2: Add renderCollection function**

```javascript
function renderCollection() {
  const owned = state.monsters;
  let html = `
    <div class="collection-header">
      <button class="btn btn-back" onclick="showScreen('title-screen')">Back</button>
      <h2>\u{1F47E} Your Monsters</h2>
      <span style="color:#FFD700">\u{1FA99} ${state.coins}</span>
    </div>
    <div class="monster-grid">
  `;

  MONSTERS.forEach(def => {
    const isOwned = owned.find(m => m.id === def.id);
    const isSelected = state.selectedMonster === def.id;
    const isLocked = !isOwned;

    if (isLocked) {
      html += `
        <div class="monster-card locked">
          <div class="m-emoji">${def.emoji}</div>
          <div class="m-name">???</div>
          <div class="m-locked-text">\u{1F512} Beat Lv.${def.unlockLevel}</div>
        </div>`;
    } else {
      const evolved = isOwned.evolved;
      const emoji = evolved ? def.evolveEmoji : def.emoji;
      const name = evolved ? def.evolveName : def.name;
      const battles = isOwned.battles;
      html += `
        <div class="monster-card ${isSelected ? 'selected' : 'owned'}" onclick="selectMonster(${def.id})">
          <div class="m-emoji">${emoji}</div>
          <div class="m-name">${name}</div>
          <div class="m-level" style="color:${evolved ? '#FFD700' : '#4CAF50'}">${evolved ? '\u{2B50} Evolved' : `${battles}/20 battles`}</div>
        </div>`;
    }
  });

  html += '</div>';

  // Evolution panel for selected monster
  const selectedDef = MONSTERS[state.selectedMonster];
  const selectedOwned = owned.find(m => m.id === state.selectedMonster);
  if (selectedOwned && !selectedOwned.evolved) {
    const progress = Math.min(100, (selectedOwned.battles / 20) * 100);
    html += `
      <div class="evolution-panel">
        <h3>${selectedDef.emoji} ${selectedDef.name} Evolution</h3>
        <div class="evolution-bar"><div class="evolution-fill" style="width:${progress}%"></div></div>
        <div class="evolution-label">${selectedOwned.battles}/20 battles — Evolve into ${selectedDef.evolveName}!</div>
      </div>`;
  } else if (selectedOwned && selectedOwned.evolved) {
    html += `
      <div class="evolution-panel">
        <h3>${selectedDef.evolveEmoji} ${selectedDef.evolveName}</h3>
        <div class="evolution-label">\u{2B50} Fully evolved!</div>
      </div>`;
  }

  document.getElementById('collection-screen').innerHTML = html;
}

function selectMonster(id) {
  if (!state.unlockedMonsters.includes(id)) return;
  state.selectedMonster = id;
  saveState();
  renderCollection();
}

// Override showScreen to render on show
const _origShowScreen = showScreen;
showScreen = function(id) {
  if (id === 'collection-screen') renderCollection();
  _origShowScreen(id);
};
```

- [ ] **Step 3: Test collection — open collection, verify monsters show, tap to select, evolution bar appears**

Click "Collection" on title screen. Verify Flamey shows as owned/selected, locked monsters show "Beat Lv.X". Tap a locked monster — nothing happens. Verify evolution bar shows 0/20.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add monster collection screen with selection and evolution progress"
```

---

### Task 6: Times table select screen

**Files:**
- Modify: `index.html` (add table screen CSS + render function)

- [ ] **Step 1: Add table select CSS**

```css
/* Table Select */
#table-screen {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  padding: 16px;
}
.table-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
}
.table-card {
  background: rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}
.table-card.active { border-color: #FFD700; background: rgba(255,215,0,0.15); }
.table-card.locked { opacity: 0.3; cursor: default; }
.table-card .t-num { font-size: 28px; font-weight: bold; color: #fff; }
.table-card .t-label { font-size: 11px; color: #888; margin-top: 4px; }
.table-card.locked .t-label { color: #f44336; }
```

- [ ] **Step 2: Add renderTableSelect and selectTable functions**

```javascript
function renderTableSelect() {
  let html = `
    <div class="collection-header">
      <button class="btn btn-back" onclick="showScreen('battle-screen');renderBattle()">Back</button>
      <h2>\u{1F4D6} Times Tables</h2>
    </div>
    <div class="table-grid">
  `;

  TABLE_ORDER.forEach(table => {
    const unlockLevel = TABLE_UNLOCK_LEVELS[table];
    const isUnlocked = state.level > unlockLevel;
    const isActive = state.selectedTable === table;

    html += `
      <div class="table-card ${isActive ? 'active' : ''} ${isUnlocked ? '' : 'locked'}"
           onclick="${isUnlocked ? `selectTable(${table})` : ''}">
        <div class="t-num">x${table}</div>
        <div class="t-label">${isUnlocked ? (isActive ? 'Selected' : 'Unlocked') : `\u{1F512} Lv.${unlockLevel + 1}`}</div>
      </div>`;
  });

  html += '</div>';
  document.getElementById('table-screen').innerHTML = html;
}

function selectTable(table) {
  state.selectedTable = table;
  saveState();
  renderTableSelect();
}

// Also show table select from battle topbar — add to showScreen
const _prevShowScreen = showScreen;
showScreen = function(id) {
  if (id === 'collection-screen') renderCollection();
  if (id === 'table-screen') renderTableSelect();
  _prevShowScreen(id);
};
```

- [ ] **Step 3: Make the times table display in battle topbar tappable**

In `renderBattle`, update the topbar to include an onclick on the table span:

```javascript
// In renderBattle, change the table display to:
`<span style="cursor:pointer;text-decoration:underline" onclick="showScreen('table-screen')">x${state.selectedTable} Table \u{25B6}</span>`
```

- [ ] **Step 4: Test — open table select from battle, verify locked/unlocked states, tap to change table**

Start a battle, tap the "x1 Table" text in the topbar. Verify table select screen opens with x1 selected, others locked. Can't select locked tables.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add times table select screen with progressive unlock"
```

---

### Task 7: Colour palette + visual polish

**Files:**
- Modify: `index.html` (update CSS colours, add polish)

- [ ] **Step 1: Update colour palette**

Replace the title screen gradient and adjust colours for a cohesive cartoon battle theme:

```css
/* Updated title screen */
#title-screen {
  background: linear-gradient(180deg, #FF6B6B 0%, #FF8E53 50%, #FFE66D 100%);
}

/* Updated battle screen */
#battle-screen {
  background: linear-gradient(180deg, #74b9ff 0%, #74b9ff 55%, #55efc4 55%, #00b894 100%);
}

/* Answer buttons - varied colours */
.answer-btn:nth-child(1) { background: #e17055; box-shadow: 0 4px 0 #d63031; }
.answer-btn:nth-child(2) { background: #0984e3; box-shadow: 0 4px 0 #074c8c; }
.answer-btn:nth-child(3) { background: #6c5ce7; box-shadow: 0 4px 0 #4834d4; }
```

- [ ] **Step 2: Add comic-style damage text ("POW!", "ZAP!")**

Update `submitAnswer` to show fun text on hits:

```javascript
// In submitAnswer, replace showDamageText calls with:
const attackWords = ['POW!', 'ZAP!', 'WHAM!', 'BAM!', 'BOOM!'];
const hitWord = attackWords[Math.floor(Math.random() * attackWords.length)];
showDamageText(enemyMonster, hitWord, '#FFD700'); // for correct
// and
showDamageText(playerMonster, 'OUCH!', '#f44336'); // for wrong
```

- [ ] **Step 3: Add a hit-flash overlay on monsters when damaged**

Add to CSS:

```css
@keyframes hitFlash {
  0% { filter: brightness(1); }
  50% { filter: brightness(2) saturate(0); }
  100% { filter: brightness(1); }
}
.hit-flash { animation: hitFlash 0.2s ease; }
```

In `submitAnswer`, add `classList.add('hit-flash')` to the hit monster's emoji element, remove after 200ms.

- [ ] **Step 4: Visual check — open in browser, verify colours look cohesive and fun**

Play through 2-3 battles. Check: title screen gradient, battle background, answer button colours, damage text, hit flash.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: apply cartoon battle colour palette and visual polish"
```

---

### Task 8: Responsive design + touch targets

**Files:**
- Modify: `index.html` (add media queries)

- [ ] **Step 1: Add responsive CSS**

```css
/* Mobile-first responsive */
@media (max-width: 480px) {
  .question-text { font-size: 26px; }
  .answer-btn { padding: 12px 24px; font-size: 20px; min-width: 70px; }
  .monster-emoji { font-size: 52px !important; }
  .vs-text { font-size: 24px; }
  #title-screen h1 { font-size: 32px; }
  .title-monster { font-size: 80px; }
}

@media (min-width: 768px) {
  .question-text { font-size: 40px; }
  .answer-btn { padding: 18px 48px; font-size: 28px; }
  .monster-emoji { font-size: 80px !important; }
  .hp-bar { width: 120px; }
}

/* Ensure minimum 44px touch targets */
.answer-btn { min-height: 44px; }
.btn { min-height: 44px; }
.monster-card { min-height: 44px; }
.table-card { min-height: 44px; }
```

- [ ] **Step 2: Test on mobile viewport (Chrome DevTools device mode)**

Open Chrome DevTools, toggle device toolbar, test at iPhone SE (375px), iPhone 14 (390px), iPad (768px). Verify buttons are tappable, text is readable, layout doesn't overflow.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add responsive design for mobile and tablet"
```

---

### Task 9: Final testing + edge cases

**Files:**
- Modify: `index.html` (any fixes found)

- [ ] **Step 1: Test full game loop**

1. Fresh start — title screen loads
2. Tap "Battle!" — battle screen shows with Flamey vs random enemy
3. Answer 3 correct in a row — streak bonus coins shown on win
4. Answer wrong — HP drops, enemy attacks
5. Die — lose screen, tap "Try Again", restart same level
6. Win — coins increase, level advances
7. Play to level 5 — boss battle triggers
8. Beat boss — new monster unlocked notification
9. Go to Collection — new monster visible, can select it
10. Start battle with new monster — different stats
11. Play to 20 battles with one monster — evolution triggers
12. Close browser, reopen — all progress preserved

- [ ] **Step 2: Test edge cases**

- Negative answer options never appear (test with table x1, a=1 => correct=1, wrongs should be positive)
- Boss HP is 2x normal
- Can't select locked monsters
- Can't select locked tables
- Streak resets on wrong answer

- [ ] **Step 3: Add meta tags for PWA-like experience**

Add to `<head>`:

```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#FF6B6B">
<meta name="description" content="Learn multiplication by battling cute monsters! Free, no ads, no data collection.">
```

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: final testing, edge case fixes, and meta tags"
```
