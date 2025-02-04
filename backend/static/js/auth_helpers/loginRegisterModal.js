$(document).ready(function() {
  window.addEventListener('supabaseClientReady', async function() {
    const currentEmail = await window.supabaseClient.getCurrentUserEmail();
    if (!currentEmail) {
      var loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
      $('#loginModal').modal('show');
      return;
    }
    return;
  });
});
document.addEventListener('DOMContentLoaded', function () {
  document.querySelector('#registerModalShowLink').addEventListener('click', function() {
    $('#loginModal').modal('hide');
    var signUpModal = new bootstrap.Modal(document.getElementById('signUpModal'));
    $('#signUpModal').modal('show');
  });
  document.querySelector('#loginModalShowLink').addEventListener('click', function() {
    $('#signUpModal').modal('hide');
    var loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    $('#loginModal').modal('show');
  });
  async function handleLoginModalFormSubmission() {
      const loginForm = document.getElementById('loginModal');
      if (!loginForm) {
          return;
      }
      loginForm.addEventListener('submit', async function(event) {
          event.preventDefault();
          const email = document.getElementById('loginModalEmail').value;
          const password = document.getElementById('loginModalPassword').value;
          try {
              const { user, session, error } = await window.supabaseClient.signInWithEmail(email, password);
              if (error) throw error;
              localStorage.setItem("ageConfirmed", "true");
              window.location.reload();
          } catch (error) {
              console.error('Login error:', error.message);
              alert('Login failed: ' + error.message);
          }
      }, false);
  }
  async function submitRegistrationModalForm() {
    const registerForm = document.getElementById('signUpModalForm');
    registerForm.addEventListener('submit', async function(event) {
      event.preventDefault();
      const formData = new FormData(registerForm);
      const userDetails = {
          email: formData.get('signUpModalEmail'),
          password: formData.get('signUpModalPassword'),
          confirmPassword: formData.get('signUpModalPasswordRepeat'),
          username: formData.get('signUpModalUsername'),
          name: formData.get('signUpModalName'),
          zip_code: formData.get('signUpModalZipCode'),
          phone: formData.get('signUpModalPhone'),
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
          window.location.reload();
      } catch (error) {
          alert('Registration failed. Please try again');
      }
    });
  }
  async function handleModalPasswordReset() {
    var myForgotPassowrdModal = new bootstrap.Modal(document.getElementById('forgotPasswordLoginModal'));
    var email = document.getElementById('forgotPasswordEmail').value;
    try {
      await window.supabaseClient.sendResetPassword(email);
      alert('Password reset email sent successfully, be sure to log in and reset your password from the same device.');
    } catch (error) {
      console.error('Error:', error.message);
    } finally {
      myForgotPassowrdModal.hide();
    }
  }
  window.addEventListener('load', function() {
    handleLoginModalFormSubmission();
    submitRegistrationModalForm();
  }, false);
  document.querySelector('#forgotPasswordModalLink').addEventListener('click', function() {
    $('#loginModal').modal('hide');
    var forgotPasswordModal = new bootstrap.Modal(document.getElementById('forgotPasswordLoginModal'));
    $('#forgotPasswordLoginModal').modal('show');
  });
  const forgotPasswordForm = document.getElementById('forgotPasswordModalForm');
  forgotPasswordForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    const email = document.getElementById('forgotPasswordEmail').value;
    if (email) {
      handleModalPasswordReset();
    }
  });
  $('#loginModal').on('hidden.bs.modal', async function () {
    const currentUserEmail = await window.supabaseClient.getCurrentUserEmail();
    if (!currentUserEmail && !$('#loginModal').hasClass('show') && !$('#signUpModal').hasClass('show') && !$('#forgotPasswordLoginModal').hasClass('show')) {
      $('#signUpModal').modal('show');
    }
  });
  $('#signUpModal').on('hidden.bs.modal', async function () {
    const currentUserEmail = await window.supabaseClient.getCurrentUserEmail();
    if (!currentUserEmail && !$('#loginModal').hasClass('show') && !$('#signUpModal').hasClass('show') && !$('#forgotPasswordLoginModal').hasClass('show')) {
      $('#loginModal').modal('show');
    }
  });
  $('#forgotPasswordLoginModal').on('hidden.bs.modal', async function () {
    const currentUserEmail = await window.supabaseClient.getCurrentUserEmail();
    if (!currentUserEmail && !$('#loginModal').hasClass('show') && !$('#signUpModal').hasClass('show') && !$('#forgotPasswordLoginModal').hasClass('show')) {
      $('#loginModal').modal('show');
    }
  });
});
