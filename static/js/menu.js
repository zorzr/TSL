var toggled = false;

function isVisible(component) {
    return getComputedStyle(component, null).display != "none";
}

function isMobile() {
    button = document.getElementById("nav-button");
    return isVisible(button);
}

function adjustMenu() {
    banner = document.getElementById("banner");
    if (!isMobile() && !isVisible(banner)) {
        banner.style.display = "block";
        toggled = false;
    } else if (isMobile() && isVisible(banner) && !toggled) {
        banner.style.display = "none";
    }
}

function toggleMenu() {
    banner = document.getElementById("banner");
    if (toggled) {
        banner.style.display = "none";
        toggled = false;
    } else {
        banner.style.display = "block";
        toggled = true;
    }
}

window.addEventListener('resize', adjustMenu, true)