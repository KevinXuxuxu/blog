// var dark_css_path;
// var light_css_path;

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