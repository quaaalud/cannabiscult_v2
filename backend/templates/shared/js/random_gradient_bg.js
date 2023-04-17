const stage = document.querySelector('.stage');

const bodyRange = document.createRange();
bodyRange.setStart(document.body, 0);

function parse(str) {
  const frag = bodyRange.createContextualFragment(str);
  return frag.firstElementChild;
}

const backgrounds = ['sunny', 'ocean', 'day', 'swamp', 'dawn', 'love'];

function randomBackground() {
  const currentClass = stage.classList[1];
  const otherBackgrounds = backgrounds.filter(b => b !== currentClass);
  const randomClass = otherBackgrounds[Math.floor(Math.random() * otherBackgrounds.length)];
  stage.classList.remove(currentClass);
  stage.classList.add(randomClass);
}

function clear() {
  stage.innerHTML = '';
}

requestAnimationFrame(() => {
  randomBackground();
});

document.addEventListener('click', () => {
  randomBackground();
});