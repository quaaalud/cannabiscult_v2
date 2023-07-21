fetch('/config')
    var _supabase;
    .then(response => response.json())
    .then(data => {
        var SUPABASE_URL = data.SUPA_STORAGE_URL;
        var SUPABASE_KEY = data.SUPA_PUBLIC_KEY;
        const supabase = _supabase.createClient(SUPABASE_URL, SUPABASE_KEY, {
            auth: {
                autoRefreshToken: false,
                persistSession: false,
                detectSessionInUrl: false
            }
        }
    );
    

    window.userToken = null
    
    document.addEventListener('DOMContentLoaded', function (event) {
      var signUpForm = document.querySelector('#sign-up')
      signUpForm.onsubmit = signUpSubmitted.bind(signUpForm)
    
      var logInForm = document.querySelector('#log-in')
      logInForm.onsubmit = logInSubmitted.bind(logInForm)
    
      var userDetailsButton = document.querySelector('#user-button')
      userDetailsButton.onclick = fetchUserDetails.bind(userDetailsButton)
    
      var logoutButton = document.querySelector('#logout-button')
      logoutButton.onclick = logoutSubmitted.bind(logoutButton)
    })
    
    const signUpSubmitted = (event) => {
      event.preventDefault()
      const email = event.target[0].value
      const password = event.target[1].value
    
      supabase.auth
        .signUp({ email, password })
        .then((response) => {
          response.error ? alert(response.error.message) : setToken(response)
        })
        .catch((err) => {
          alert(err)
        })
    }
    
    const logInSubmitted = (event) => {
      event.preventDefault()
      const email = event.target[0].value
      const password = event.target[1].value
    
      supabase.auth
        .signIn({ email, password })
        .then((response) => {
          response.error ? alert(response.error.message) : setToken(response)
        })
        .catch((err) => {
          alert(err.response.text)
        })
    }
    
    const fetchUserDetails = () => {
      alert(JSON.stringify(supabase.auth.user()))
    }
    
    const logoutSubmitted = (event) => {
      event.preventDefault()
    
      supabase.auth
        .signOut()
        .then((_response) => {
          document.querySelector('#access-token').value = ''
          document.querySelector('#refresh-token').value = ''
          alert('Logout successful')
        })
        .catch((err) => {
          alert(err.response.text)
        })
    }
    
    function setToken(response) {
      if (response.user.confirmation_sent_at && !response?.session?.access_token) {
        alert('Confirmation Email Sent')
      } else {
        document.querySelector('#access-token').value = response.session.access_token
        document.querySelector('#refresh-token').value = response.session.refresh_token
        alert('Logged in as ' + response.user.email)
      }
    }
  }
);