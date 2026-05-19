const canvas = document.querySelector("#board");
const ctx = canvas.getContext("2d");
const scoreEl = document.querySelector("#score");
const bestEl = document.querySelector("#best");
const overlay = document.querySelector("#overlay");
const overlayTitle = document.querySelector("#overlay-title");
const overlayText = document.querySelector("#overlay-text");
const startButton = document.querySelector("#start-button");
const pauseButton = document.querySelector("#pause-button");
const restartButton = document.querySelector("#restart-button");

const gridSize = 20;
const tileCount = canvas.width / gridSize;
const tickMs = 110;
const vectors = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

let snake;
let food;
let direction;
let nextDirection;
let score;
let best = loadBestScore();
let timer = null;
let state = "ready";

bestEl.textContent = best;
resetGame();
draw();

function resetGame() {
  snake = [
    { x: 10, y: 10 },
    { x: 9, y: 10 },
    { x: 8, y: 10 },
  ];
  direction = vectors.right;
  nextDirection = vectors.right;
  score = 0;
  food = randomFood();
  scoreEl.textContent = score;
}

function startGame() {
  if (state === "running") return;
  if (state === "gameover") resetGame();
  state = "running";
  overlay.classList.add("is-hidden");
  pauseButton.textContent = "Pause";
  clearInterval(timer);
  timer = setInterval(step, tickMs);
  draw();
}

function pauseGame() {
  if (state === "running") {
    state = "paused";
    clearInterval(timer);
    timer = null;
    pauseButton.textContent = "Resume";
    showOverlay("Paused", "Press Resume or space to keep playing.", "Resume");
    return;
  }

  if (state === "paused") startGame();
}

function restartGame() {
  clearInterval(timer);
  timer = null;
  state = "ready";
  resetGame();
  showOverlay("Snake", "Press Start or use an arrow key.", "Start");
  draw();
}

function step() {
  direction = nextDirection;
  const head = {
    x: snake[0].x + direction.x,
    y: snake[0].y + direction.y,
  };

  const willEat = head.x === food.x && head.y === food.y;

  if (hasHitWall(head) || hasHitSelf(head, willEat)) {
    endGame();
    return;
  }

  snake.unshift(head);

  if (willEat) {
    score += 10;
    scoreEl.textContent = score;
    if (score > best) {
      best = score;
      saveBestScore(best);
      bestEl.textContent = best;
    }
    food = randomFood();
  } else {
    snake.pop();
  }

  draw();
}

function draw() {
  ctx.fillStyle = "#182026";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  drawFood();
  drawSnake();
}

function drawGrid() {
  ctx.strokeStyle = "#26343a";
  ctx.lineWidth = 1;
  for (let i = 0; i <= tileCount; i += 1) {
    const pos = i * gridSize + 0.5;
    ctx.beginPath();
    ctx.moveTo(pos, 0);
    ctx.lineTo(pos, canvas.height);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, pos);
    ctx.lineTo(canvas.width, pos);
    ctx.stroke();
  }
}

function drawSnake() {
  snake.forEach((segment, index) => {
    const inset = index === 0 ? 2 : 3;
    ctx.fillStyle = index === 0 ? "#65d46e" : "#2a9f47";
    roundedRect(
      segment.x * gridSize + inset,
      segment.y * gridSize + inset,
      gridSize - inset * 2,
      gridSize - inset * 2,
      5,
    );
    ctx.fill();
  });
}

function drawFood() {
  const cx = food.x * gridSize + gridSize / 2;
  const cy = food.y * gridSize + gridSize / 2;
  ctx.fillStyle = "#f25f4c";
  ctx.beginPath();
  ctx.arc(cx, cy, gridSize * 0.36, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#ffd166";
  ctx.beginPath();
  ctx.arc(cx - 3, cy - 3, gridSize * 0.12, 0, Math.PI * 2);
  ctx.fill();
}

function roundedRect(x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.arcTo(x + width, y, x + width, y + height, radius);
  ctx.arcTo(x + width, y + height, x, y + height, radius);
  ctx.arcTo(x, y + height, x, y, radius);
  ctx.arcTo(x, y, x + width, y, radius);
  ctx.closePath();
}

function randomFood() {
  let candidate;
  do {
    candidate = {
      x: Math.floor(Math.random() * tileCount),
      y: Math.floor(Math.random() * tileCount),
    };
  } while (snake.some((segment) => segment.x === candidate.x && segment.y === candidate.y));
  return candidate;
}

function setDirection(name) {
  const vector = vectors[name];
  if (!vector) return;
  const isReverse = vector.x + direction.x === 0 && vector.y + direction.y === 0;
  if (isReverse) return;
  nextDirection = vector;
  if (state === "ready" || state === "gameover") startGame();
}

function hasHitWall(head) {
  return head.x < 0 || head.y < 0 || head.x >= tileCount || head.y >= tileCount;
}

function hasHitSelf(head, willEat) {
  const body = willEat ? snake : snake.slice(0, -1);
  return body.some((segment) => segment.x === head.x && segment.y === head.y);
}

function endGame() {
  clearInterval(timer);
  timer = null;
  state = "gameover";
  pauseButton.textContent = "Pause";
  showOverlay("Game Over", `Score: ${score}`, "Play Again");
}

function showOverlay(title, text, buttonText) {
  overlayTitle.textContent = title;
  overlayText.textContent = text;
  startButton.textContent = buttonText;
  overlay.classList.remove("is-hidden");
}

document.addEventListener("keydown", (event) => {
  const keys = {
    ArrowUp: "up",
    w: "up",
    W: "up",
    ArrowDown: "down",
    s: "down",
    S: "down",
    ArrowLeft: "left",
    a: "left",
    A: "left",
    ArrowRight: "right",
    d: "right",
    D: "right",
  };

  if (event.key === " ") {
    event.preventDefault();
    pauseGame();
    return;
  }

  if (keys[event.key]) {
    event.preventDefault();
    setDirection(keys[event.key]);
  }
});

document.querySelectorAll("[data-dir]").forEach((button) => {
  button.addEventListener("click", () => setDirection(button.dataset.dir));
});

startButton.addEventListener("click", startGame);
pauseButton.addEventListener("click", pauseGame);
restartButton.addEventListener("click", restartGame);

function loadBestScore() {
  try {
    return Number(window.localStorage.getItem("snake-best") || 0);
  } catch {
    return 0;
  }
}

function saveBestScore(value) {
  try {
    window.localStorage.setItem("snake-best", String(value));
  } catch {
    // Some file:// browser contexts block localStorage. The current run can still play.
  }
}
