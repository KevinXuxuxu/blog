const url = window.location.href;
const no_giscus = !url.slice(20).startsWith('/blog/post/');

function setCookie(cName, cValue, expDays) {
    let date = new Date();
    date.setTime(date.getTime() + (expDays * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = cName + "=" + cValue + "; " + expires + "; path=/";
}

function getCookie(cName, default_value) {
    const name = cName + "=";
    const cDecoded = decodeURIComponent(document.cookie); //to be careful
    const cArr = cDecoded.split('; ');
    let res = default_value;
    cArr.forEach(val => {
        if (val.indexOf(name) === 0) res = val.substring(name.length);
    })
    return res;
}

function reload_script(old_script, new_theme) {
    // This is to switch giscus theme
    var new_script = document.createElement('script');
    Array.from(old_script.attributes).forEach(attr => new_script.setAttribute(attr.name, attr.value));
    new_script.setAttribute('data-theme', new_theme);
    old_script.parentNode.replaceChild(new_script, old_script);
}

function change_color_theme(color_theme, init) {
    var moon = document.getElementById('moon');
    var checkbox = document.getElementById('theme-checkbox');
    var giscus_script = document.getElementById('giscus');
    if (color_theme === 'dark') {
        checkbox.checked = true;
        moon.textContent = '🌖';
        if (!no_giscus) {
            reload_script(giscus_script, 'catppuccin_macchiato');
        }
    } else {
        checkbox.checked = false;
        moon.textContent = '🌒';
        if (!no_giscus) {
            reload_script(giscus_script, 'catppuccin_latte');
        }
    }
    if (init) {
        checkbox.removeAttribute('disabled');
    }
}

function set_color_theme(color_theme) {
    setCookie('color_theme', color_theme, 30);
    document.documentElement.setAttribute('data-theme', color_theme);
    change_color_theme(color_theme, false);
}

function get_initial_color_theme() {
    var color_theme = getCookie('color_theme');
    if (color_theme === undefined) {
        color_theme = 'light';
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            color_theme = 'dark';
        }
    }
    return color_theme;
}

function init_color_theme() {
    var color_theme = get_initial_color_theme();
    document.documentElement.setAttribute('data-theme', color_theme);
}

function init_color_switch() {
    var color_theme = get_initial_color_theme();
    change_color_theme(color_theme, true);
}

function switch_color_theme() {
    let color_theme = getCookie('color_theme', 'light');
    if (color_theme === 'dark') {
        set_color_theme('light');
    } else {
        set_color_theme('dark');
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const element = document.getElementById("color-switch");
    const giscus_script = document.getElementById("giscus");
    if (element && (no_giscus || giscus_script)) {
        init_color_switch();
    }
});

window.matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", (event) => {
        const theme = event.matches ? "dark" : "light";
        set_color_theme(theme);
    });