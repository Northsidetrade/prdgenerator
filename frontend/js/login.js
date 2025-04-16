/**
 * Login form handler for PRD Generator
 * Following Semantic Seed Coding Standards for JavaScript implementation
 */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorAlert = document.getElementById('login-error');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Check for redirect parameter
    const urlParams = new URLSearchParams(window.location.search);
    const redirectPage = urlParams.get('redirect');
    
    // If user is already logged in, redirect
    if (window.AuthModule && window.AuthModule.isAuthenticated()) {
        redirectAfterLogin(redirectPage);
    }
    
    /**
     * Handle login form submission
     */
    async function handleLogin(event) {
        event.preventDefault();
        
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        
        // Basic form validation
        if (!emailInput.value || !passwordInput.value) {
            showError('Please enter both email and password.');
            return;
        }
        
        try {
            // Show loading state
            const submitButton = loginForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...';
            
            // Attempt login
            await window.AuthModule.loginUser(emailInput.value, passwordInput.value);
            
            // Hide error if it was shown
            hideError();
            
            // Redirect after successful login
            redirectAfterLogin(redirectPage);
            
        } catch (error) {
            console.error('Login error:', error);
            showError('Invalid email or password. Please try again.');
            
            // Reset button
            const submitButton = loginForm.querySelector('button[type="submit"]');
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        if (errorAlert) {
            errorAlert.textContent = message;
            errorAlert.classList.remove('d-none');
        }
    }
    
    /**
     * Hide error message
     */
    function hideError() {
        if (errorAlert) {
            errorAlert.classList.add('d-none');
        }
    }
    
    /**
     * Redirect after successful login
     */
    function redirectAfterLogin(redirectPage) {
        if (redirectPage) {
            window.location.href = redirectPage;
        } else {
            window.location.href = '../templates/generate.html';
        }
    }
});
