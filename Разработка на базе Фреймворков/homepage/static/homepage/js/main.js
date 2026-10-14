document.addEventListener("DOMContentLoaded", function () {
    var yearNode = document.getElementById("current-year");
    if (yearNode) {
        yearNode.textContent = String(new Date().getFullYear());
    }
});
