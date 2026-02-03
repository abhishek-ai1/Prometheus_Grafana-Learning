// Authentication Helper Script
// Include this at the end of each page that requires authentication

const AUTH_TOKEN_KEY = 'authToken';
const USER_KEY = 'user';
const PERMISSIONS_KEY = 'permissions';

// Check authentication on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAuthUI);
} else {
    initializeAuthUI();
}

function initializeAuthUI() {
    checkAuthentication();
    setupLogout();
    applyRoleBasedVisibility();
}

function checkAuthentication() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    
    if (!token) {
        // Not authenticated, redirect to login
        window.location.href = '/login.html';
        return;
    }
    
    // Display user info
    const user = JSON.parse(localStorage.getItem(USER_KEY) || '{}');
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay) {
        userDisplay.textContent = `👤 ${user.name || user.email || 'User'} (${user.role || 'Unknown'})`;
    }
}

function applyRoleBasedVisibility() {
    const user = JSON.parse(localStorage.getItem(USER_KEY) || '{}');
    const permissions = JSON.parse(localStorage.getItem(PERMISSIONS_KEY) || '{}');
    
    // Hide admin-only elements for non-admin users
    if (user.role !== 'admin') {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = 'none';
        });
    }
}

function setupLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

async function logout() {
    // Clear local storage
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(PERMISSIONS_KEY);
    
    // Redirect to login
    window.location.href = '/login.html';
}

// Helper function to get auth token for API calls
function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

// Helper function to get user info
function getUser() {
    return JSON.parse(localStorage.getItem(USER_KEY) || '{}');
}

// Helper function to get permissions
function getPermissions() {
    return JSON.parse(localStorage.getItem(PERMISSIONS_KEY) || '{}');
}

// Helper function to check if user is admin
function isAdmin() {
    const user = getUser();
    return user.role === 'admin';
}

// Helper function to check if user has permission
function hasPermission(tab) {
    const permissions = getPermissions();
    return permissions.accessible_tabs && permissions.accessible_tabs.includes(tab);
}

// Fetch wrapper that includes auth token
async function authorizedFetch(url, options = {}) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return fetch(url, {
        ...options,
        headers,
    });
}
