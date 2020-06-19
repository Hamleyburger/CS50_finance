function validateRegister(form) {

    // Renaming vars for easier readability
    usernameElement = document.getElementById("username");
    passwordElement = document.getElementById("password");
    confirmElement = document.getElementById("confirm_password");
    username = usernameElement.value;
    password = passwordElement.value;
    password_confirm = confirmElement.value;
    
    // Reset invalid values before checking
    usernameElement.classList.remove("is-invalid");
    passwordElement.classList.remove("is-invalid");
    confirmElement.classList.remove("is-invalid");
    
    // flag will be false if any check fails and onsubmit will return false
    var flag = true;

    if (username == "") {
        usernameElement.classList.add("is-invalid");
        document.getElementById("username-feedback").innerHTML = "You must provide a username";
        flag = false;
    }
    else if (!(username.length >= 4 && username.length <= 30)) {
        usernameElement.classList.add("is-invalid");
        document.getElementById("username-feedback").innerHTML = "Username must be between 4 and 30 characters long";
        flag = false;
    }

    if (password == "") {
        passwordElement.classList.add("is-invalid");
        document.getElementById("password-feedback").innerHTML = "You must provide a password";
        flag = false;
    }
    else if (!(password.length > 7)) {
        passwordElement.classList.add("is-invalid");
        document.getElementById("password-feedback").innerHTML = "Your password must be at least 8 characters long";
        flag = false;
    }

    if (password_confirm == "") {
        confirmElement.classList.add("is-invalid");
        document.getElementById("confirm-feedback").innerHTML = "You must provide a password";
        flag = false;
    }
    else if (password !== password_confirm) {
        confirmElement.classList.add("is-invalid");
        document.getElementById("confirm-feedback").innerHTML = "The passwords didn't match";
        flag = false;
    }

    return flag;
}


function validateLogin(form) {

    // Renaming vars for easier readability
    usernameElement = document.getElementById("username");
    passwordElement = document.getElementById("password");
    username = usernameElement.value;
    password = passwordElement.value;

    // Reset invalid values before checking
    usernameElement.classList.remove("is-invalid");
    passwordElement.classList.remove("is-invalid");

    // flag will be false if any check fails and onsubmit will return false
    var flag = true;

    if (username == "") {
        usernameElement.classList.add("is-invalid");
        document.getElementById("username-feedback").innerHTML = "You must provide a username";
        flag = false;
    }
    else if (!(username.length >= 4 && username.length <= 30)) {
        usernameElement.classList.add("is-invalid");
        document.getElementById("username-feedback").innerHTML = "Username must be between 4 and 30 characters long";
        flag = false;
    }

    if (password == "") {
        passwordElement.classList.add("is-invalid");
        document.getElementById("password-feedback").innerHTML = "You must provide a password";
        flag = false;
    }
    else if (!(password.length > 7)) {
        passwordElement.classList.add("is-invalid");
        document.getElementById("password-feedback").innerHTML = "Your password must be at least 8 characters long";
        flag = false;
    }

    return flag;
}







