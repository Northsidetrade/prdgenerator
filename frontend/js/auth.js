/**
 * Authentication module for PRD Generator
 * Handles user authentication, token management, and UI state
 */

// API Configuration
const API_URL = 'http://localhost:8000/api/v1';
const AUTH_TOKEN_KEY = 'prd_generator_auth_token';
const USER_DATA_KEY = 'prd_generator_user_data';

// UI Elements
const authButtonsElement = document.getElementById('auth-buttons');
const userProfileElement = document.getElementById('user-profile');
const usernameElement = document.getElementById('username');
const logoutButtonElement = document.getElementById('logout-button');
const generateNavElement = document.getElementById('nav-generate');
const historyNavElement = document.getElementById('nav-history');

/**
 * Initialize authentication state
 */
function initAuth() {
    // Check if user is logged in
    const token = getAuthToken();
    const userData = getUserData();
    
    if (token && userData) {
        // Update UI for authenticated user
        showAuthenticatedUI(userData);
        
        // Verify token validity with backend
        verifyToken(token)
            .catch(error => {
                console.error('Token validation failed:', error);
                logout();
            });
    } else {
        // Show unauthenticated UI
        showUnauthenticatedUI();
    }
    
    // Set up logout button
    if (logoutButtonElement) {
        logoutButtonElement.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
    
    // Set up auth-required page redirection
    checkRequiredAuth();
}

/**
 * Check if page requires authentication and redirect if needed
 */
function checkRequiredAuth() {
    // Array of pages that require authentication
    const authRequiredPages = [
        'generate.html',
        'history.html',
        'profile.html'
    ];
    
    const currentPage = window.location.pathname.split('/').pop();
    
    if (authRequiredPages.includes(currentPage) && !isAuthenticated()) {
        window.location.href = '../templates/login.html?redirect=' + currentPage;
    }
}

/**
 * Show UI elements for authenticated users
 */
function showAuthenticatedUI(userData) {
    if (authButtonsElement) authButtonsElement.classList.add('d-none');
    if (userProfileElement) userProfileElement.classList.remove('d-none');
    if (usernameElement) usernameElement.textContent = userData.full_name || userData.email;
    
    // Enable restricted navigation
    if (generateNavElement) generateNavElement.classList.remove('d-none');
    if (historyNavElement) historyNavElement.classList.remove('d-none');
}

/**
 * Show UI elements for unauthenticated users
 */
function showUnauthenticatedUI() {
    if (authButtonsElement) authButtonsElement.classList.remove('d-none');
    if (userProfileElement) userProfileElement.classList.add('d-none');
    
    // Disable restricted navigation
    if (generateNavElement) generateNavElement.classList.add('d-none');
    if (historyNavElement) historyNavElement.classList.add('d-none');
}

/**
 * Verify token validity with backend
 */
async function verifyToken(token) {
    const response = await fetch(`${API_URL}/users/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Token verification failed');
    }
    
    return response.json();
}

/**
 * Send login request to API
 */
async function loginUser(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Login failed');
    }
    
    const data = await response.json();
    
    // Save token and user data
    setAuthToken(data.access_token);
    
    // Fetch user details
    const userResponse = await fetch(`${API_URL}/users/me`, {
        headers: {
            'Authorization': `Bearer ${data.access_token}`
        }
    });
    
    if (!userResponse.ok) {
        throw new Error('Failed to fetch user data');
    }
    
    const userData = await userResponse.json();
    setUserData(userData);
    
    return userData;
}

/**
 * Send registration request to API
 */
async function registerUser(fullName, email, password) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            full_name: fullName,
            email: email,
            password: password
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
    }
    
    return response.json();
}

/**
 * Log out the current user
 */
function logout() {
    // Clear auth data
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
    
    // Update UI
    showUnauthenticatedUI();
    
    // Redirect to home page
    window.location.href = '../index.html';
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!getAuthToken();
}

/**
 * Get the current auth token
 */
function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Set the auth token
 */
function setAuthToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
}

/**
 * Get the current user data
 */
function getUserData() {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
}

/**
 * Set the user data
 */
function setUserData(userData) {
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(userData));
}

/**
 * Get authorization headers
 */
function getAuthHeaders() {
    const token = getAuthToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Initialize authentication on page load
document.addEventListener('DOMContentLoaded', initAuth);

// Export auth functions for use in other modules
window.AuthModule = {
    loginUser,
    registerUser,
    logout,
    isAuthenticated,
    getAuthToken,
    getAuthHeaders,
    getUserData
};
