import init, { initThreadPool, PlayerWASM } from '/static/wasm/cosmo_rayon/cosmo.js';
await init();
await initThreadPool(navigator.hardwareConcurrency);
async function readScene(name) {
    try {
        const response = await fetch('/static/cosmo_scenes/' + name + '.cos');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();
        return text.split('\n').map(line => line.trim());
    } catch (error) {
        console.error('Error fetching or reading the scene file (.cos):', error);
    }
}

async function readSTL(name) {
    try {
        const response = await fetch('/static/cosmo_scenes/' + name + '.stl');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const arrayBuffer = await response.arrayBuffer();
        return new Uint8Array(arrayBuffer);
    } catch (error) {
        console.error('Error fetching or reading the STL file:', error);
    }
}

async function readSTLs(names) {
    var result = [];
    for (const name of names) {
        result.push(await readSTL(name));
    }
    return result;
}

function startCosmo(displayEle, player) {
    const intId = setInterval(() => {
        player.update();
        displayEle.textContent = player.get_a().join('\n');
    }, 1000.0 / 24.0);
    displayEle.setAttribute('intId', intId);
}

async function prepareCosmo(displayEle) {
    const sceneName = displayEle.getAttribute('scene');
    const STLNames = displayEle.hasAttribute('stl-names') ?
        displayEle.getAttribute('stl-names').split(',') : [];
    const [w, h] = displayEle.getAttribute('dimension').split(',');
    const fr = displayEle.getAttribute('framerate');
    const enableAABB = displayEle.getAttribute('enable-aabb') === 'true';
    const disableShade = displayEle.getAttribute('disable-shade') === 'true';

    const scene = await readScene(sceneName);
    const STLData = await readSTLs(STLNames);
    const player = PlayerWASM.new(scene, parseInt(fr), parseInt(w), parseInt(h), enableAABB, disableShade, STLNames, STLData);
    startCosmo(displayEle, player);
    displayEle.addEventListener('click', () => {
        if (displayEle.hasAttribute('intId')) {
            clearInterval(displayEle.getAttribute('intId'));
            displayEle.removeAttribute('intId');
        } else {
            startCosmo(displayEle, player);
        }
    });
}

function loadCosmo() {
    if (window.cosmoLoaded) {
        return;
    }
    console.log('loading cosmo...')
    let displayEles = document.getElementsByClassName('cosmo-display');
    for (let i = 0; i < displayEles.length; ++i) {
        prepareCosmo(displayEles[i]);
    }
    window.cosmoLoaded = true;
}

window.cosmoLoaded = false;
window.addEventListener('load', loadCosmo);
if (window.loaded) {
    loadCosmo();
}
