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
    const formData = new FormData(registerForm);
    const userDetails = {
        email: formData.get('register_email'),
        password: formData.get('register_password'),
        confirmPassword: formData.get('register_repeat_password'),
        username: formData.get('register_username'),
        name: formData.get('register_name'),
        zip_code: formData.get('register_zip_code'),
        phone: formData.get('register_phone'),
        type: "user"
    };
    try {
        if (window.supabaseClient.checkUserStatus() === true) {
          alert('You are already registered. Login or use the Password Reset if needed.');
          return;
        }
        const user = await window.supabaseClient.registerUser(userDetails);
        await fetch('/users/create_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userDetails),
        });
        alert('Registration successful. Check your email to confirm your registration details.');
        registerForm.reset(); 
    } catch (error) {
        alert('Registration failed. Please try again');
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
