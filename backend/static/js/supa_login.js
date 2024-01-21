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
                    break;
                case 'SIGNED_OUT':
                    this.onSignOut();
                    this.setAuthCookies(session, false);
                    break;
                case 'TOKEN_REFRESHED':
                    this.onSignIn(session);
                    this.setAuthCookies(session, true);
                    break;
                case 'PASSWORD_RECOVERY':
                    this.onPasswordRecovery(session);
                    break;
                case 'USER_UPDATED':
                    this.onUserUpdated(session);
                    break;
                default:
                    console.warn(`Unhandled auth event: ${event}`);
            }
        });
    }

    onSignIn(session) {
        console.log('User signed in');
        this.setAuthCookies(session, true);
    }
    onSignOut() {
        console.log('User signed out');
        // Need to Implement
    }
    onPasswordRecovery(session) {
        console.log('Password recovery mode');
        // Need to Implement
    }

    onUserUpdated(session) {
        console.log('User details updated');
        // Need to Implement
    }
    setAuthCookies(session, isSignIn) {
        if (isSignIn) {
            // Set cookies on sign in or token refresh
            const maxAge = 100 * 365 * 24 * 60 * 60; // 100 years, essentially never expires
            document.cookie = `my-access-token=${session.access_token}; path=/; max-age=${maxAge}; SameSite=Lax; secure`;
            document.cookie = `my-refresh-token=${session.refresh_token}; path=/; max-age=${maxAge}; SameSite=Lax; secure`;
        } else {
            // Delete cookies on sign out
            const expires = new Date(0).toUTCString();
            document.cookie = `my-access-token=; path=/; expires=${expires}; SameSite=Lax; secure`;
            document.cookie = `my-refresh-token=; path=/; expires=${expires}; SameSite=Lax; secure`;
        }
    }
    validateAndSanitizeEmail(email) {
        if (!window.validator.isEmail(email)) {
            throw new Error('Invalid email format.');
        }
        return window.validator.normalizeEmail(email, { all_lowercase: true });
    }
    
     async signInWithEmail(email, password) {
        try {
            email = this.validateAndSanitizeEmail(email);
            const { user, session, error } = await this.supabase.auth.signInWithPassword({ email, password });
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
        const email = this.validateAndSanitizeEmail(userDetails.email);
        console.log(email);
        try {
            const { user, error: authError } = await this.supabase.auth.signUp({
                email: email,
                password: userDetails.password,
                options: {
                  data: userDetails,
                },
            });
            if (authError) throw authError;

            return user;
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

    async sendResetPassword(email) {
        try {
            email = this.validateAndSanitizeEmail(email);
            console.log(this.supabase);
            const { error } = await this.supabase.auth.resetPasswordForEmail(email, { redirectTo: '/profile_settings' });
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
    
    async updateUserPasswordWithToken(token, type, newPassword) {
        try {
            if (type !== 'recovery') throw new Error('Invalid request type.');
            const { data, error } = this.supabase.auth.verifyOtp({ token_hash: token, type: type});
            console.log('Data ' + data);
            console.log('Error ' + error);
            this.updateUserPassword(newPassword);
            if (error) throw error;
        } catch (error) {
            console.error("Error in updateUserPasswordWithToken:", error.message);
            throw error;
        }
    }

    async getPublicUrlfromBucket(filePath) {
        try {
            const { data, error } = await this.supabase.storage.from('cannabiscult').getPublicUrl(filePath);
            if (error) throw error;
            return data.publicURL;
        } catch (error) {
            console.error('Error retrieving public URL:', error);
            throw error;
        }
    }
}

window.SupabaseClient = SupabaseClient;
