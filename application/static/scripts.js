
function validateForm(form) {

    var flag = true;

    username = form.username.value;
    if (!(username.length >= 4 && username.length <= 30)) {
        var username = document.getElementById("username");
        username.classList.add("is-invalid");
        document.getElementById("username-feedback").innerHTML = "Username must be between 4 and 30 characters long"
        flag = false;
    }

    pw = form.password.value;
    if (!(pw.length > 7)) {
        var password = document.getElementById("password");
        password.classList.add("is-invalid");
        document.getElementById("password-feedback").innerHTML = "Your password must be at least 8 characters long"
        flag = false;
    }

    if (form.password.value !== form.confirm_password.value) {
        var confirm_password = document.getElementById("confirm_password");
        confirm_password.classList.add("is-invalid");
        document.getElementById("confirm-feedback").innerHTML = "The passwords didn't match"
        flag = false;
    }

    if (form.username.value == "") {
        document.getElementById("username-feedback").innerHTML = "You must provide a username";
        username.classList.add("is-invalid");
        flag = false;
    }

    if (form.password.value == "") {
        document.getElementById("password-feedback").innerHTML = "You must provide a password";
        password.classList.add("is-invalid");
        flag = false;
    }

    if (form.confirm_password.value == "") {
        document.getElementById("confirm-feedback").innerHTML = "You must provide a password";
        confirm_password.classList.add("is-invalid");
        flag = false;
    }

    return flag;
}
