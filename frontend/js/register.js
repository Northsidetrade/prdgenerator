/**
 * Registration form handler for PRD Generator
 * Following Semantic Seed Coding Standards for JavaScript implementation
 */

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const errorAlert = document.getElementById('register-error');
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }
    
    /**
     * Handle registration form submission
     */
    async function handleRegistration(event) {
        event.preventDefault();
        
        const fullNameInput = document.getElementById('full_name');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        
        // Validate form data
        if (!fullNameInput.value || !emailInput.value || !passwordInput.value || !confirmPasswordInput.value) {
            showError('Please fill out all fields.');
            return;
        }
        
        if (passwordInput.value !== confirmPasswordInput.value) {
            showError('Passwords do not match.');
            return;
        }
        
        if (passwordInput.value.length < 8) {
            showError('Password must be at least 8 characters long.');
            return;
        }
        
        try {
            // Show loading state
            const submitButton = registerForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating account...';
            
            // Attempt registration
            await window.AuthModule.registerUser(
                fullNameInput.value,
                emailInput.value,
                passwordInput.value
            );
            
            // Hide error if it was shown
            hideError();
            
            // After successful registration, log the user in
            try {
                await window.AuthModule.loginUser(emailInput.value, passwordInput.value);
                
                // Redirect to PRD generation page
                window.location.href = '../templates/generate.html';
                
            } catch (loginError) {
                console.error('Auto-login error:', loginError);
                
                // If auto-login fails, still consider registration successful
                // but redirect to login page
                window.location.href = 'login.html?registered=true';
            }
            
        } catch (error) {
            console.error('Registration error:', error);
            
            let errorMessage = 'Registration failed. Please try again.';
            
            // Check for specific error messages from API
            if (error.message.includes('already exists')) {
                errorMessage = 'An account with this email already exists.';
            }
            
            showError(errorMessage);
            
            // Reset button
            const submitButton = registerForm.querySelector('button[type="submit"]');
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
});
