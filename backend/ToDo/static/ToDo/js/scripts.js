function hide_modal() {
    overlay = document.getElementById("overlay");
    form = overlay.querySelector("form");

    overlay.classList.add("hidden")
    form.removeAttribute("action");
}

function show_modal(action) {
    overlay = document.getElementById("overlay");
    form = overlay.querySelector("form");

    overlay.classList.remove("hidden")
    form.setAttribute("action", action);
}