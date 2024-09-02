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

function set_color_theme(color_theme) {
    setCookie('color_theme', color_theme, 30);
    var moon = document.getElementById('moon');
    var checkbox = document.getElementById('theme-checkbox');
    document.documentElement.setAttribute('data-theme', color_theme);
    if (color_theme === 'dark') {
        checkbox.checked = true;
        moon.textContent = '🌖';
    } else {
        checkbox.checked = false;
        moon.textContent = '🌒';
    }
}

function init_color_theme() {
    var color_theme = getCookie('color_theme', 'light');
    document.documentElement.setAttribute('data-theme', color_theme);
}

function init_color_switch() {
    var color_theme = getCookie('color_theme', 'light');
    var moon = document.getElementById('moon');
    var checkbox = document.getElementById('theme-checkbox');
    if (color_theme === 'dark') {
        checkbox.checked = true;
        moon.textContent = '🌖';
    } else {
        checkbox.checked = false;
        moon.textContent = '🌒';
    }
    checkbox.removeAttribute('disabled');
}

function switch_color_theme() {
    let color_theme = getCookie('color_theme', 'light');
    if (color_theme === 'dark')  {
        set_color_theme('light');
    } else {
        set_color_theme('dark');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const element = document.getElementById("color-switch");
    if (element) {
        init_color_switch();
    }
});