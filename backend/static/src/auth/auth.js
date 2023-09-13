var _supabase = supabase;

fetch('/config')
    .then(response => response.json())
    .then(data => {
        var SUPABASE_URL = data.SUPA_STORAGE_URL;
        var SUPABASE_KEY = data.SUPA_PUBLIC_KEY;

        window.supabase = _supabase.createClient(SUPABASE_URL, SUPABASE_KEY, {
            auth: {
                autoRefreshToken: false,
                persistSession: false,
                detectSessionInUrl: false
            }
        });
        
        const supabase = window.supabase
    
    window.userToken = null;
        
    function setToken(response) {
      if (response.user.confirmation_sent_at && !response?.session?.access_token) {
        alert('Confirmation Email Sent');
      } else {
        document.cookie = `access_token=${response.session.access_token}; Secure; HttpOnly; SameSite=Lax;`;
        alert('Logged in as ' + response.user.email);
      }
    }
    
    function isLoggedIn() {
      return !!window.supabase.auth.user();
    }
}); 