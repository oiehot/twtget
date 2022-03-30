function getParams() {
    var scripts = document.getElementsByTagName('script');
    var lastScript = scripts[scripts.length-1];
    var scriptName = lastScript;
    return {
        userId : scriptName.getAttribute('user_id')
    };
}

function saveScrollPosition() {
    y = window.scrollY;
    user_id = getParams().userId;
    key = `twitter_${user_id}_scrollPosition`;
    value = y.toString();
    localStorage.setItem(key, value);
    // console.log(`Save ScrollPosition: ${key} : ${value}`);
}

function restoreScrollPosition() {
    user_id = getParams().userId;
    key = `twitter_${user_id}_scrollPosition`;
    value = Number(localStorage.getItem(key));
    window.scrollTo(0, value);
    console.log(`Restore ScrollPosition: ${key} : ${value}`)
}

window.addEventListener("beforeunload", function (e) {
    saveScrollPosition();
});

window.addEventListener("scroll", function (e) {
    saveScrollPosition();
});

document.addEventListener("DOMContentLoaded", function () {
    restoreScrollPosition();
});