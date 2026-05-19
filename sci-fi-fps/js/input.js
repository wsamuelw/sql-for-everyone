export const inputState = {
  keys: new Map(),
  mouseDown: false,
  wheelDelta: 0,
};

export function setupInput() {
  document.addEventListener('keydown', (e) => {
    inputState.keys.set(e.code, true);
  });

  document.addEventListener('keyup', (e) => {
    inputState.keys.delete(e.code);
  });

  document.addEventListener('mousedown', (e) => {
    if (e.button === 0) inputState.mouseDown = true;
  });

  document.addEventListener('mouseup', (e) => {
    if (e.button === 0) inputState.mouseDown = false;
  });

  document.addEventListener('wheel', (e) => {
    inputState.wheelDelta = e.deltaY;
  });
}

export function isKeyDown(code) {
  return inputState.keys.has(code);
}
