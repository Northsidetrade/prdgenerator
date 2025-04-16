/**
 * Main application file for PRD Generator
 * Following Semantic Seed Coding Standards for JavaScript implementation
 */

// Global API configuration
const API_URL = 'http://localhost:8000/api/v1';

// Document Ready Handler
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Update UI based on authentication state
    updateUIForAuthState();

    // Initialize page-specific functionality
    initializeCurrentPage();
});

/**
 * Update UI elements based on authentication state
 */
function updateUIForAuthState() {
    const isAuthenticated = window.AuthModule && window.AuthModule.isAuthenticated();
    const authRequiredPages = ['generate.html', 'history.html', 'profile.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    // Clear CTA buttons on homepage if authenticated
    if (currentPage === 'index.html' || currentPage === '') {
        const ctaButtons = document.getElementById('cta-buttons');
        if (ctaButtons && isAuthenticated) {
            ctaButtons.innerHTML = `
                <a class="btn btn-primary btn-lg" href="templates/generate.html" role="button">Generate PRD</a>
                <a class="btn btn-secondary btn-lg" href="templates/history.html" role="button">View My PRDs</a>
            `;
        }
    }
    
    // Redirect to login if page requires authentication
    if (authRequiredPages.includes(currentPage) && !isAuthenticated) {
        window.location.href = '../templates/login.html?redirect=' + currentPage;
    }
}

/**
 * Initialize page-specific functionality
 */
function initializeCurrentPage() {
    const currentPage = window.location.pathname.split('/').pop();
    
    // Handle login page "registered" query parameter
    if (currentPage === 'login.html') {
        const urlParams = new URLSearchParams(window.location.search);
        const registered = urlParams.get('registered');
        
        if (registered === 'true') {
            const alertContainer = document.createElement('div');
            alertContainer.className = 'alert alert-success alert-dismissible fade show';
            alertContainer.innerHTML = `
                Registration successful! Please log in with your new account.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            const loginForm = document.getElementById('login-form');
            if (loginForm) {
                loginForm.parentNode.insertBefore(alertContainer, loginForm);
            }
        }
    }
}

/**
 * Handle API errors consistently
 */
function handleApiError(error, defaultMessage = 'An error occurred. Please try again.') {
    console.error('API Error:', error);
    
    // Extract error message from the API response if available
    let errorMessage = defaultMessage;
    if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
    } else if (error.message) {
        errorMessage = error.message;
    }
    
    return errorMessage;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + 
           date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Get template display name
 */
function getTemplateDisplayName(templateType) {
    const templates = {
        'crud_application': 'CRUD Application',
        'ai_agent': 'AI Agent',
        'saas_platform': 'SaaS Platform',
        'custom': 'Custom Template'
    };
    
    return templates[templateType] || templateType;
}
