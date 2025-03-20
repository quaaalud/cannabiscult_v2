export function initializeSupabaseClient() {
    const client = new window.SupabaseClient();
    client.initialize().then(() => {
        window.supabaseClient = client;
        window.signInWithGoogleGlobal = client.signInWithGoogle;
        window.dispatchEvent(new CustomEvent('supabaseClientReady'));
    }).catch(e => console.error("Initialization failed:", e));
}

class SupabaseClient {
    constructor() {
        this.supabase = null;
        this.currentUser = null;
        this.session = null;
    }

    async loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
            document.head.appendChild(script);
        });
    }

    async loadValidator() {
        await this.loadScript('https://cdn.jsdelivr.net/npm/validator@13.7.0/validator.min.js');
    }

    async loadSupabase() {
        await this.loadScript("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2");
        return window.supabase;
    }
    
    async loadGoogleOauth() {
        await this.loadScript("https://accounts.google.com/gsi/client");
        window.google.accounts.id.initialize({
            client_id: this.config.GOOGLE_CLIENT_ID,
            callback: this.signInWithGoogle.bind(this),
        });
        const googleAuthButton = `
          <div id="g_id_onload"
            data-client_id="${this.config.GOOGLE_CLIENT_ID}"
            data-context="signin"
            data-ux_mode="popup"
            data-auto_prompt="false">
         </div>
          <div class="g_id_signin"
            data-type="standard"
            data-shape="pill"
            data-theme="outline"
            data-text="signin_with"
            data-size="large"
            data-logo_alignment="left">
          </div>
        `
        const loginWithGoogleContainer = document.getElementById('googleSignInContainer');
        if (loginWithGoogleContainer) {
            loginWithGoogleContainer.innerHTML = googleAuthButton;
            setTimeout(() => {
                window.google.accounts.id.renderButton(loginWithGoogleContainer.querySelector('.g_id_signin'), {
                    theme: "outline",
                    size: "large",
                });
            }, 100);
        };
        const signupWithGoogleContainer = document.getElementById('googleSignUpContainer');
        if (signupWithGoogleContainer) {
            signupWithGoogleContainer.innerHTML = googleAuthButton;
            setTimeout(() => {
                window.google.accounts.id.renderButton(signupWithGoogleContainer.querySelector('.g_id_signin'), {
                    theme: "outline",
                    size: "large",
                });
            }, 100);
        };
    }

    async getConfig() {
        try {
            const response = await fetch('/config');
            if (!response.ok) throw new Error('Failed to fetch configuration.');
            this.config = await response.json();
        } catch (error) {
            console.error("Failed to fetch config:", error);
            throw error;
        }
    }

    async initialize() {
        try {
            await this.getConfig();
            await this.loadSupabase();
            await this.loadValidator();
            await this.loadGoogleOauth();
            this.supabase = window.supabase.createClient(this.config.SUPA_STORAGE_URL, this.config.SUPA_PUBLIC_KEY);
            this.initializeAuthListeners();
        } catch (error) {
            console.error("Failed to load scripts:", error);
            throw error;
        }
    }

    initializeAuthListeners() {
        this.supabase.auth.onAuthStateChange((event, session) => {
            switch (event) {
                case 'INITIAL_SESSION':
                    window.dispatchEvent(new CustomEvent('userAuthChange'));
                    if (session && session.user) {
                        this.currentUser = session.user;
                        this.session = session;
                    }
                    break;
                case 'SIGNED_IN':
                    this.onSignIn(session);
                    this.addLogoutLink();
                    break;
                case 'TOKEN_REFRESHED':
                    this.onSignIn(session);
                    this.addLogoutLink();
                    break;
                case 'SIGNED_OUT':
                    this.onSignOut(session);
                    window.dispatchEvent(new CustomEvent('userAuthChange'));
                    break;
                case 'PASSWORD_RECOVERY':
                    this.onPasswordRecovery(session);
                    break;
                case 'USER_UPDATED':
                    this.onUserUpdated(session);
                    this.removeloginLink();
                    this.addLogoutLink();
                    break;
                default:
                    console.warn(`Unhandled auth event: ${event}`);
            }
        });
    }
    onSignIn(session) {
      if (!session || !session.user) {
          console.error('Invalid session data received during sign-in.');
          return;
      }
      if (!this.currentUser) {
        window.dispatchEvent(new CustomEvent('userAuthChange'));
      }
      this.currentUser = session.user;
      this.session = session;
      try {
        this.removeloginLink();
        this.setAuthCookies(session, true);
        const isSuperuser = this.checkSuperuserStatus();
        if (isSuperuser) {
            this.addStrainSubmissionsLink();
        }
      } catch (error) {
        console.error('Error setting auth cookies:', error);
      }
    }
    onSignOut(session) {
        this.currentUser = null;
        this.setAuthCookies(session, false);
        this.clearStorage();
        this.removeLogoutLink();
    }
    onPasswordRecovery(session) {
        console.log('Password recovery mode');
    }
    onUserUpdated(session) {
        console.log('User details updated');
        this.setAuthCookies(session, true);
    }
    clearStorage() {
        [window.localStorage, window.sessionStorage].forEach(storage => {
            Object.keys(storage).forEach(key => storage.removeItem(key));
        });
    }
    setAuthCookies(session, isSignIn) {
        if (isSignIn) {
            // Set cookies on sign in or token refresh
            const maxAge = 100 * 365 * 24 * 60 * 60; // 100 years, essentially never expires
            document.cookie = `my-access-token=${session.access_token}; path=/; max-age=${maxAge}; SameSite=Lax; secure`;
            document.cookie = `my-refresh-token=${session.refresh_token}; path=/; max-age=${maxAge}; SameSite=Lax; secure`;
        } else {
            const expires = new Date(0).toUTCString();
            document.cookie = `my-access-token=; path=/; expires=${expires}; SameSite=Lax; secure`;
            document.cookie = `my-refresh-token=; path=/; expires=${expires}; SameSite=Lax; secure`;
        }
    }
    isUserLoggedIn() {
        return !!this.currentUser;
    }
    validateFormData(data) {
        if (data.password !== data.confirmPassword || !this.validatePassword(data.password)) {
          return false;
        }
        data.email = this.validateAndSanitizeEmail(data.email);
        data.name = this.sanitizeString(data.name);
        data.username = this.sanitizeString(data.username);
        data.zip_code = this.sanitizeString(data.zip_code);
        data.phone = this.sanitizeString(data.phone);
        data.type = "user";
        return data;
    }
    
    validateAndSanitizeEmail(email) {
        if (!window.validator.isEmail(email)) {
            throw new Error('Invalid email format.');
        }
        return window.validator.normalizeEmail(email, { all_lowercase: true });
    }
    validatePassword(password) {
        const hasMinLength = window.validator.isLength(password, { min: 6 });
        const hasUpper = /[A-Z]/.test(password); // At least one uppercase letter
        const hasLower = /[a-z]/.test(password); // At least one lowercase letter
        const hasNumberOrSpecial = /[0-9!@#$%^&*]/.test(password); // At least one number or standard special character

        if (!hasMinLength || !hasUpper || !hasLower || !hasNumberOrSpecial) {
            return false;
        }
        return true;
    }
    sanitizeString(str) {
        if (typeof str !== 'string') {
            return '';
        }
        return str.trim().replace(/<[^>]*>?/gm, '');
    }
    sanitizeInputString(input) {
      return input.replace(/[^a-zA-Z0-9 ]/g, '');
    }
    getAccessToken() {
        return this.session ? this.session.access_token : null;
    }
    async signInUserToServer(email, password) {
         const response = await fetch('/users/', {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json'
           },
           body: JSON.stringify({ email: email, password: password })
         });      
    }
    async googleCallbackAfterSignin() {
        const response = await fetch('/users/callback/google', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: email, password: password })
        });  
    }
    async signInWithEmail(email, password) {
        try {
            email = this.validateAndSanitizeEmail(email);
            await this.signInUserToServer(email, password)
            const { user, session, error } = await this.supabase.auth.signInWithPassword({ email, password }, { redirectTo: 'https://cannabiscult.co/home' });
            if (error) throw error;
            this.session = session;
            return { user, session };
        } catch (error) {
            console.error("Error in signInWithEmail:", error.message);
            throw error;
        }
    }
    async signInWithGoogle(response) {
        try {
              const { data, error } = await supabase.auth.signInWithIdToken({
                provider: 'google',
                token: response.credential,
              });
        } catch (error) {
            console.error("Error in signInWithGoogle:", error.message);
            throw error;
        }
    }
    async updateLastLogin(userId) {
        try {
            const { error } = await this.supabase
                .from('users')
                .update({ last_login: new Date().toISOString() })
                .eq('id', userId);

            if (error) throw error;
        } catch (error) {
            console.error("Error updating last login:", error.message);
            throw error;
        }
    }
    async registerUser(userDetails) {
      if (!this.validateFormData(userDetails)) {
        throw new Error('Invalid user data.');
      }
      try {
          const { data, error } = await this.supabase.auth.signUp({
            email: userDetails.email,
            password: userDetails.password,
            options: {
              data: {
                name: userDetails.name,
                username: userDetails.username,
                zip_code: userDetails.zip_code,
                phone: userDetails.phone,
              }
            },
          })
          if (error) throw error;
          return data ? data.user : null;
      } catch (error) {
        console.error('Error in registerUser:', error.message);
        throw new Error('Registration failed.');
      }
    }

    async signOut() {
        try {
            const { error } = await this.supabase.auth.signOut();
            if (error) throw error;
            await fetch('/users/logout/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
           });
        } catch (error) {
            console.error("Error in signOut:", error.message);
            throw error;
        }
    }
    encodeEmail(email) {
        return btoa(email);
    }
    async checkSuperuserStatus() {
      try {
          const { data: { user } } = await this.supabase.auth.getUser();
          if (user === null) {
              return false;
          }
          if (user && user.id) {
              const response = await fetch('/users/super_user_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: user.id })
              });
              if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
              }
              const data = await response.json();
              if (data.supuser_status === true) {
                  return true;
              }
              return false;
          } else {
              return false;
          }
      } catch (error) {
          console.error("Error checking superuser status:", error.message);
          return false;
      }
    }
    getUserIdFromToken() {
        try {
            const tokenKey = Object.keys(window.localStorage).find(key => key.endsWith('-auth-token'));
            if (!tokenKey) {
                return null;
            }
            const tokenString = window.localStorage.getItem(tokenKey);
            if (!tokenString) {
                return null;
            }
            const tokenObj = JSON.parse(tokenString);
            return tokenObj && tokenObj.user && tokenObj.user.id ? tokenObj.user.id : null;
        } catch (error) {
            console.error('Error retrieving user id from token:', error);
            return null;
        }
    }
    async checkUserStatus() {
      const userId = this.getUserIdFromToken();
      if (!userId) { return; };
      try {
          const response = await fetch(`/users/get_user_by_id?user_id=${userId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
          });
          if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          if (data && data.username) {
              return true;
          }
          return false;
      } catch (error) {
          return false;
      }
    }
    async sendResetPassword(email) {
        try {
            email = this.validateAndSanitizeEmail(email);
            const { error } = await this.supabase.auth.resetPasswordForEmail(email, { redirectTo: 'https://cannabiscult.co/forgot-password' });
            if (error) throw error;
        } catch (error) {
            console.error("Error in resetPassword:", error.message);
            throw error;
        }
    }
    async updateUserPassword(newPassword) {
        try {
            const { error } = await this.supabase.auth.updateUser({ password: newPassword });
            if (error) throw error;
        } catch (error) {
            console.error("Error in updateUserPassword:", error.message);
            throw error;
        }
    }
    async addLogoutLink() {
      const navlinks = document.getElementById('navLinksList');
      if (navlinks == null) {
        return;
      }
      if (!navlinks.querySelector('#logoutLink')) {
          const logoutListItem = document.createElement('li');
          const logoutLink = document.createElement('a');
          logoutLink.id = 'logoutLink';
          logoutLink.href = '#';
          logoutLink.textContent = 'Log Out';
          logoutLink.classList.add('nav-link');
          logoutLink.setAttribute('data-bs-toggle', 'modal');
          logoutLink.setAttribute('data-bs-target', '#logoutModal');
          logoutListItem.appendChild(logoutLink);
          navlinks.appendChild(logoutListItem);
          window.dispatchEvent(new CustomEvent('userAuthChange'));
      }
    }
    async addLoginLink() {
        const navBar = document.querySelector('.navbar-nav');
        if (!document.getElementById('loginLink')) {
            const loginListItem = document.createElement('li');
            loginListItem.className = 'nav-item';
            const loginLink = document.createElement('a');
            loginLink.id = 'loginLink';
            loginLink.href = '/login'; // Set to your login route
            loginLink.textContent = 'Login/Register';
            loginLink.className = 'nav-link active';
            loginListItem.appendChild(loginLink);
            navBar.appendChild(loginListItem);
        }
    }
    async addStrainSubmissionsLink() {
        const navLinksList = document.getElementById('navLinksList');
        if (!navLinksList.querySelector('#myRankingsLink')) {
            const linkItem = document.createElement('li');
            const link = document.createElement('a');
            link.id = 'myRankingsLink';
            link.href = '/home';
            link.textContent = 'My Rankings';
            link.className = 'nav-link';
            navLinksList.appendChild(linkItem);
            linkItem.appendChild(link);
        }
    }
    async removeLogoutLink() {
        const logoutLink = document.getElementById('logoutLink');
        if (logoutLink) {
            logoutLink.parentNode.remove();
        }
        this.removeStrainSubmissionLink();
    }
    async removeStrainSubmissionLink() {
        const submissionLink = document.getElementById('myRankingsLink');
        if (submissionLink) {
            submissionLink.parentNode.remove();
        }
    }
    async removeloginLink() {
        const loginLink = document.getElementById('loginLink');
        if (loginLink) {
            loginLink.parentNode.remove();
        }
    }
    async getPublicUrlfromBucket(filePath) {
        try {
            const { data, error } = await this.supabase.storage.from('cc_public').getPublicUrl(filePath);
            if (error) throw error;
            return data.publicURL;
        } catch (error) {
            console.error('Error retrieving public URL:', error);
            throw error;
        }
    }
    async getCurrentUserEmail() {
      const { data: { user }, error } = await this.supabase.auth.getUser();
      if (error || !user) {
        return;
      } else {
        return user.email;
      }
    }
    async getCurrentUserId() {
      const { data: { user }, error } = await this.supabase.auth.getUser();
      if (error || !user) {
        return;
      } else {
        return user.id;
      }
    }
    async checkUserAuthentication() {
        try {
            const { data: { user }, error } = await this.supabase.auth.getUser();
            if (!user) {
                const urlParams = new URLSearchParams(window.location.search);
                const resetTokenType = urlParams.get('type');
                if (resetTokenType === 'recovery') {
                  return;
                }
                window.location.href = '/login';
                return;
            } else {
              return user.email;
            }
            if (error) {
                alert('Authentication error. Please try logging in again.', error);
                window.location.href = '/login';
                return;
            }
        } catch (error) {
            alert('An unexpected error occurred. Please try again.');
            window.location.href = '/login';
            return;
        }
    }
    async fetchImageUrls(productType, productId) {
      const fullUrl = `/images/${productType}/${productId}/`;
      try {
        const response = await fetch(fullUrl);
        if (!response.ok) {
          throw new Error(`Server error! Status: ${response.status}`);
        }
        const imageUrls = await response.json();
        return imageUrls;
      } catch (error) {
        console.error('Fetch error:', error);
        return [];
      }
    }
    async updateCarouselWithImages(imageUrls) {
      const carouselIndicators = document.querySelector('.carousel-indicators');
      const carouselInner = document.querySelector('.carousel-inner');
    
      imageUrls.forEach((url, index) => {
        const slideIndex = index + 1;
    
        const newIndicator = document.createElement('button');
        newIndicator.setAttribute('type', 'button');
        newIndicator.setAttribute('data-mdb-target', '#carouselImages');
        newIndicator.setAttribute('data-mdb-slide-to', slideIndex.toString());
        newIndicator.setAttribute('aria-label', `Slide ${slideIndex + 1}`);
        if (index === 0) {
          newIndicator.classList.add('active');
        }
        carouselIndicators.appendChild(newIndicator);
    
        const newItem = document.createElement('div');
        newItem.className = 'carousel-item'
        newItem.setAttribute('data-mdb-interval', '10000');
        newItem.innerHTML = `<img src="${url}" class="d-block w-100 img-fluid rounded-5" alt="Image ${slideIndex + 1}">`;
        carouselInner.appendChild(newItem);
      });
    }
}
window.SupabaseClient = SupabaseClient;
