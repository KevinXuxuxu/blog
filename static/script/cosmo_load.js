import init, { PlayerWASM } from '/static/wasm/cosmo/cosmo.js';
await init();
async function readScene(id) {
    try {
        const response = await fetch('/static/cosmo_scenes/' + id + '.cos');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();
        return text.split('\n').map(line => line.trim());
    } catch (error) {
        console.error('Error fetching or reading the text file:', error);
    }
}
async function prepareCosmo(displayEle) {
    let [id, w, h] = displayEle.id.split('-');
    const scene = await readScene(id);
    const player = PlayerWASM.new(scene, 24, parseInt(w), parseInt(h), false, false, false);
    player.update();
    displayEle.textContent = player.get_a().join('\n');
    displayEle.addEventListener('click', () => {
        if (displayEle.hasAttribute('intId')) {
            clearInterval(displayEle.getAttribute('intId'));
            displayEle.removeAttribute('intId');
        } else {
            const intId = setInterval(() => {
                player.update();
                displayEle.textContent = player.get_a().join('\n');
            }, 1000.0 / 24.0);
            displayEle.setAttribute('intId', intId);
        }
    });
}

window.onload = function () {
    let displayEles = document.getElementsByClassName('cosmo-display');
    for (let i = 0; i < displayEles.length; ++i) {
        prepareCosmo(displayEles[i]);
    }
};