export function initializeSupabaseClient() {
    const client = new window.SupabaseClient();
    client.initialize().then(() => {
        window.supabaseClient = client;
        window.dispatchEvent(new CustomEvent('supabaseClientReady'));
    }).catch(e => console.error("Initialization failed:", e));
}

class SupabaseClient {
    constructor() {
        this.supabase = null;
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
                    break;
                case 'SIGNED_IN':
                    this.onSignIn(session);
                    this.addLogoutLink();
                    break;
                case 'SIGNED_OUT':
                    this.onSignOut(session);
                    break;
                case 'TOKEN_REFRESHED':
                    this.onSignIn(session);
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
        console.log('User signed out');
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
    validateFormData(data) {
        // Password validation
        if (data.password !== data.confirmPassword || !this.validatePassword(data.password)) {
          return false; // Either passwords do not match or password validation failed
        }
        // Email sanitization
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
            return false; // Password does not meet the criteria
        }
        return true; // Password is valid
    }
    sanitizeString(str) {
        if (typeof str !== 'string') {
            return '';
        }
        return str.trim().replace(/<[^>]*>?/gm, ''); // Basic HTML tag stripping
    }
    
    sanitizeInputString(input) {
      return input.replace(/[^a-zA-Z0-9 ]/g, '');
    }
    
     async signInWithEmail(email, password) {
        try {
            email = this.validateAndSanitizeEmail(email);
            const { user, session, error } = await this.supabase.auth.signInWithPassword({ email, password }, { redirectTo: 'https://cannabiscult.co/home' });
            if (error) throw error;
            return { user, session };
        } catch (error) {
            console.error("Error in signInWithEmail:", error.message);
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

          return true;
      } catch (error) {
        console.error('Error in registerUser:', error.message);
        throw new Error('Registration failed.');
      }
    }

    async signOut() {
        try {
            const { error } = await this.supabase.auth.signOut();
            if (error) throw error;
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
          // Retrieve the user object
          
          const { data: { user } } = await this.supabase.auth.getUser();
          
          if (user === null) {
              return false;
          }
          if (user && user.email) {
              // Construct the URL for the FastAPI endpoint
              const response = await fetch('/users/super_user_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: this.encodeEmail(user.email) })
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

    async checkUserStatus() {
      try {
          const response = await fetch('/users/get_username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: this.encodeEmail(user.email) })
          });
          if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          if (data.username) {
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
      // Check if the 'footerLinks' element exists
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
            link.className = 'nav-link'; // Add any additional classes as per your CSS framework
            navLinksList.appendChild(linkItem);
            linkItem.appendChild(link);
        }
    }

    async removeLogoutLink() {
        const logoutLink = document.getElementById('logoutLink');
        if (logoutLink) {
            logoutLink.parentNode.remove();
        }
        removeStrainSubmissionLink();
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

    async checkUserAuthentication() {
        try {
            const { data: { user }, error } = await this.supabase.auth.getUser();

            if (!user) {
                const urlParams = new URLSearchParams(window.location.search);
                const resetTokenType = urlParams.get('type');
                if (resetTokenType === 'recovery') {
                  console.log('Recovery mode is active.');
                  return
                }
                console.log('No user logged in. Redirecting to login page.');
                window.location.href = '/login';
                return; // Stop execution if there's no user
            } else {
              return user.email;
            }
            if (error) {
                alert('Authentication error. Please try logging in again.', error);
                window.location.href = '/login';
                return;
            }
        } catch (error) {
            console.error('An error occurred while checking user authentication:', error);
            alert('An unexpected error occurred. Please try again.');
            window.location.href = '/login';
            return;
        }
    }
    async fetchImageUrls(productType, productId) {
      const fullUrl = `/images/${productType}/${productId}`;
    
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
    
      // Start adding new items from index 0 for image URLs, but account for existing carousel item
      imageUrls.forEach((url, index) => {
        const slideIndex = index + 1; // Adjust index for carousel items (starting from 1)
    
        // Add new indicator only for additional images
        const newIndicator = document.createElement('button');
        newIndicator.setAttribute('type', 'button');
        newIndicator.setAttribute('data-mdb-target', '#carouselImages');
        newIndicator.setAttribute('data-mdb-slide-to', slideIndex.toString());
        newIndicator.setAttribute('aria-label', `Slide ${slideIndex + 1}`);
        if (index === 0) { // Make the first additional image indicator active if it's the only image
          newIndicator.classList.add('active');
        }
        carouselIndicators.appendChild(newIndicator);
    
        // Add new carousel item
        const newItem = document.createElement('div');
        newItem.className = 'carousel-item'
        newItem.setAttribute('data-mdb-interval', '10000');
        newItem.innerHTML = `<img src="${url}" class="d-block w-100 img-fluid rounded-5" alt="Image ${slideIndex + 1}">`;
        carouselInner.appendChild(newItem);
      });
    }
}
window.SupabaseClient = SupabaseClient;
