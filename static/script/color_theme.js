function setCookie(cName, cValue, expDays) {
    let date = new Date();
    date.setTime(date.getTime() + (expDays * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = cName + "=" + cValue + "; " + expires + "; path=/";
}

function getCookie(cName) {
    const name = cName + "=";
    const cDecoded = decodeURIComponent(document.cookie); //to be careful
    const cArr = cDecoded .split('; ');
    let res;
    cArr.forEach(val => {
        if (val.indexOf(name) === 0) res = val.substring(name.length);
    })
    return res;
}

function set_color_theme(color_theme) {
    setCookie('color_theme', color_theme, 30);
    var spectre_style = document.getElementById('spectre');
    var moon = document.getElementById('moon');
    if (color_theme === 'dark') {
        spectre_style.setAttribute('href', '/static/style/spectre_dark.min.css');
        moon.textContent = '🌖';
    } else {
        spectre_style.setAttribute('href', '/static/style/spectre.min.css');
        moon.textContent = '🌒';
    }
}

function init_color_theme() {
    var color_theme = getCookie('color_theme');
    if (color_theme == null || color_theme === 'light') {
        set_color_theme('light');
    } else {
        set_color_theme('dark');
    }
}

function switch_color_theme() {
    if (getCookie('color_theme') === 'dark') {
        set_color_theme('light');
    } else {
        set_color_theme('dark');
    }
}

window.onload = init_color_theme;