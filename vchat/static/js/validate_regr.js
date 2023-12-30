function clear(elm) {
    elm.value = "";
}

document.forms['register'].addEventListener("submit", function(evt) {
    const password = document.getElementById("password");
    const retype = document.getElementById("retype");
    if (password.value != retype.value) {
        evt.preventDefault();
        clear(password);
        clear(retype);
        window.alert("Passwords do not match.")
        return false;
    } else {
        return true;
    }
});