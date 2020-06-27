function validateRegister(form) {
    // TODO: Make "" not count as a failed username with ajax call

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

// This particular function uses ajax to quickly check that username exists!
$("#username").blur(function(){
        $.ajax({
            data: {
                username : $("#username").val()
            },
            url: "/ajax",
            type: "POST",
         
        }).done(function(data) {
            /* with parents().length I check if element has any parent with this ID
            because an existing username is good (green) in Login but bad (red) in register. */
            if ($("#username").parents("#loginForm").length) {
            if (data.exists) {
                    $("#username").css("border", "1px solid #4CAF50");
                    $("#username-exists").show();
                    $("#username").removeClass("is-invalid");
                    $("#username-feedback").html("");
                }
                else {
                    $("#username").css("border", "1px solid #dc3545");
                    $("#username-exists").hide();
                    $("#username").addClass("is-invalid");
                    $("#username-feedback").html("This user does not exist!");
                }
            }
            else if ($("#username").parents("#registerForm").length) {
                if (data.exists) {
                    $("#username").css("border", "1px solid #dc3545");
                    $("#username").addClass("is-invalid");
                    $("#username-feedback").html("This name is taken!");
                }
                else {
                    $("#username").css("border", "1px solid #4CAF50");
                    $("#username").removeClass("is-invalid");
                    $("#username-feedback").html("");
                }
            }
        
        });
  }); 

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



    //return flag;
}







