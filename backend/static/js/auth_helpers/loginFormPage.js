function checkFormValidity(formElement) {
    let isFormValid = true;
    const fields = formElement.querySelectorAll("input, select, textarea");
    fields.forEach((field) => {
        if (field.disabled) return;
        field.classList.remove("is-valid", "is-invalid");
        if (!field.checkValidity()) {
            field.classList.add("is-invalid");
            isFormValid = false;
        } else {
            field.classList.add("is-valid");
        }
    });
    return isFormValid;
}

async function handleLoginFormSubmission() {
    const loginForm = document.getElementById('log-in');
    if (!loginForm) {
        return;
    }
    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const email = document.getElementById('login_email').value;
        const password = document.getElementById('login_password').value;
        try {
            const { user, session, error } = await window.supabaseClient.signInWithEmail(email, password);
            if (error) throw error;
            window.location.href = "/home";
        } catch (error) {
            console.error('Login error:', error.message);
            alert('Login failed: ' + error.message);
        }
    }, false);
}

async function submitRegistrationForm() {
  const registerForm = document.getElementById('sign-up');
  registerForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    if (!checkFormValidity(registerForm)) {
      return;
    }
    const emailField = document.getElementById('register_email');
    const usernameField = document.getElementById('register_username');
    const nameField = document.getElementById('register_name');
    const zipCodeField = document.getElementById('register_zip_code');
    const phoneField = document.getElementById('register_phone');
    const passwordField = document.getElementById('register_password');
    const confirmPasswordField = document.getElementById('register_repeat_password');
    
    const email = window.validator.trim(emailField.value);
    const username = window.validator.trim(usernameField.value);
    const name = window.validator.trim(nameField.value);
    const zip_code = window.validator.trim(zipCodeField.value);
    const phone = window.validator.trim(phoneField.value);
    const password = passwordField.value;
    const confirmPassword = confirmPasswordField.value;
    
    if (!window.validator.isEmail(email)) {
      alert("Please enter a valid email address.");
      emailField.focus();
      return;
    }
    if (!window.validator.isStrongPassword(password, { 
          minLength: 6, 
          minLowercase: 1, 
          minUppercase: 1, 
          minNumbers: 1, 
          minSymbols: 0 
        })) {
      alert("Password must be at least 6 characters long and include at least one uppercase letter, one lowercase letter, and one number.");
      passwordField.focus();
      return;
    }
    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      confirmPasswordField.focus();
      return;
    }
    const userDetails = {
        email,
        password,
        confirmPassword,
        username,
        name,
        zip_code,
        phone,
        type: "user"
    };
    try {
        if (window.supabaseClient.checkUserStatus() === true) {
          alert('You are already registered. Login or use the Password Reset if needed.');
          userDetails.auth_id = window.supabaseClient.getCurrentUserId();
        } else {
          const user = await window.supabaseClient.registerUser(userDetails);
          alert('Registration successful. Check your email to confirm your registration details.');
          userDetails.auth_id = user.id;
        }
        await fetch('/users/create_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userDetails),
        });
        registerForm.reset(); 
        window.location.href = "https://cannabiscult.co/register_success/"
    } catch (error) {
        alert('Registration failed. Please try again');
        window.location.reload();
    }
  });
}

async function handlePasswordReset() {
  var myModal = new bootstrap.Modal(document.getElementById('forgotPasswordModal'));
  var email = document.getElementById('user-email').value;
  try {
    await window.supabaseClient.sendResetPassword(email);
    alert('Password reset email sent successfully, be sure to log in and reset your password from the same device.');
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    myModal.hide();
  }
}
window.addEventListener('load', function() {
  handleLoginFormSubmission();
  submitRegistrationForm();
}, false);

$(document).ready(function() {
  const forgotPasswordForm = document.getElementById('forgot-password-form');
  
  forgotPasswordForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    const email = document.getElementById('user-email').value;
    if (email) {
      handlePasswordReset();
    }
  });
  
  document.addEventListener('DOMContentLoaded', function () {
    var tabEl = document.querySelector('a[data-mdb-toggle="pill"]')
    if (tabEl) {
      var tab = new mdb.Tab(tabEl)
      tab.show()
    }
  });
});
