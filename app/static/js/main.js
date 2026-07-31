// Main JavaScript functionality for Event Review Platform

document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeAlerts();
    initializeFormValidation();
    initializePasswordToggles();
    initializeLoginForm();
    initializeRegistrationValidation();
    initializeAnimations();
});

// Navigation functionality
function initializeNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');

            navToggle.classList.toggle('active', navMenu.classList.contains('active'));
        });

        // Close mobile menu when clicking on links
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
            }

            // Close any open dropdowns when clicking outside
            const openDropdowns = document.querySelectorAll('.nav-dropdown.open');
            openDropdowns.forEach(dd => {
                if (!dd.contains(e.target)) {
                    dd.classList.remove('open');
                }
            });
        });
    }

    // Dropdown toggle click handling (for mobile/touch devices)
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const parent = toggle.closest('.nav-dropdown');
            if (!parent) return;
            // Toggle open state
            parent.classList.toggle('open');
        });
    });
}

// Alert system
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.classList.add('alert-leaving');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }

        // Auto-hide alerts after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.add('alert-leaving');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

// Show alert function for JavaScript-triggered alerts
function showAlert(type, message) {
    const flashContainer = document.querySelector('.flash-container') || document.body;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close">&times;</button>
    `;

    // Insert at the beginning of flash container or body
    flashContainer.insertBefore(alert, flashContainer.firstChild);

    // Add event listener to close button
    const closeBtn = alert.querySelector('.alert-close');
    closeBtn.addEventListener('click', () => {
        alert.classList.add('alert-leaving');
        setTimeout(() => alert.remove(), 300);
    });

    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.add('alert-leaving');
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

// Form validation and enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Real-time validation for inputs
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });

        // Enhanced form submission
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                if (submitBtn.querySelector('.btn-spinner')) {
                    return;
                }
                // Add loading state
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitBtn.disabled = true;

                // Re-enable after 10 seconds as failsafe
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 10000);
            }
        });
    });

    // Password strength indicator (only for new password creation, not sign-in/login)
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        const isLoginForm = field.closest('#loginForm') || field.autocomplete === 'current-password';
        if (field.name === 'password' && !isLoginForm) {
            field.addEventListener('input', () => showPasswordStrength(field));
        }
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }

    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }

    // Password validation
    if (field.type === 'password' && field.name === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = 'Password must be at least 6 characters long';
        }
    }

    // Password confirmation
    if (field.name === 'password2' && value) {
        const passwordField = document.querySelector('input[name="password"]');
        if (passwordField && value !== passwordField.value) {
            isValid = false;
            errorMessage = 'Passwords do not match';
        }
    }

    // Show/hide error
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }

    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);

    field.classList.add('error');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;

    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
}

function showPasswordStrength(field) {
    const value = field.value;
    let strength = 0;
    let message = '';
    let color = '';

    if (value.length >= 6) strength++;
    if (/[a-z]/.test(value)) strength++;
    if (/[A-Z]/.test(value)) strength++;
    if (/[0-9]/.test(value)) strength++;
    if (/[^A-Za-z0-9]/.test(value)) strength++;

    switch (strength) {
        case 0:
        case 1:
            message = 'Weak';
            color = '#dc2626';
            break;
        case 2:
        case 3:
            message = 'Medium';
            color = '#ca8a04';
            break;
        case 4:
        case 5:
            message = 'Strong';
            color = '#16a34a';
            break;
    }

    // Show strength indicator
    let strengthDiv = field.parentNode.querySelector('.password-strength');
    if (!strengthDiv) {
        strengthDiv = document.createElement('div');
        strengthDiv.className = 'password-strength';
        field.parentNode.appendChild(strengthDiv);
    }

    if (value.length > 0) {
        strengthDiv.innerHTML = `<div class="strength-bar"><div class="strength-fill"></div></div><span class="strength-text"></span>`;
        strengthDiv.className = `password-strength strength-${strength}`;
        strengthDiv.querySelector('.strength-text').textContent = message;
    } else {
        strengthDiv.className = 'password-strength is-hidden';
    }
}

// Animation system
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.feature-card, .stat-card, .event-card, .review-card, .dashboard-section, .event-banner, .review-form-container');
    animatedElements.forEach((el) => { el.classList.add('reveal', 'reveal-up'); observer.observe(el); });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    const time = new Date(`2000-01-01 ${timeString}`);
    return time.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        return Promise.resolve();
    }
}

// Local storage helpers
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('Local storage not available:', e);
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.warn('Local storage not available:', e);
        return defaultValue;
    }
}

// Dark mode toggle (if implemented)
function toggleDarkMode() {
    const body = document.body;
    const isDark = body.classList.toggle('dark-mode');
    setLocalStorage('darkMode', isDark);

    // Update button text/icon
    const toggleBtn = document.querySelector('.dark-mode-toggle');
    if (toggleBtn) {
        toggleBtn.innerHTML = isDark ? 
            '<i class="fas fa-sun"></i> Light Mode' : 
            '<i class="fas fa-moon"></i> Dark Mode';
    }
}

// Initialize dark mode from localStorage
function initializeDarkMode() {
    const isDark = getLocalStorage('darkMode', false);
    if (isDark) {
        document.body.classList.add('dark-mode');
    }
}

// Star rating component
class StarRating {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            maxStars: options.maxStars || 5,
            initialRating: options.initialRating || 0,
            readonly: options.readonly || false,
            size: options.size || 'medium',
            callback: options.callback || null
        };

        this.rating = this.options.initialRating;
        this.init();
    }

    init() {
        this.container.className = `star-rating ${this.options.size}`;
        this.container.innerHTML = '';

        for (let i = 1; i <= this.options.maxStars; i++) {
            const star = document.createElement('span');
            star.className = 'star';
            star.innerHTML = '★';
            star.dataset.rating = i;

            if (!this.options.readonly) {
                star.addEventListener('mouseover', () => this.highlightStars(i));
                star.addEventListener('click', () => this.setRating(i));
            }

            this.container.appendChild(star);
        }

        if (!this.options.readonly) {
            this.container.addEventListener('mouseleave', () => this.highlightStars(this.rating));
        }

        this.highlightStars(this.rating);
    }

    highlightStars(rating) {
        const stars = this.container.querySelectorAll('.star');
        stars.forEach((star, index) => {
            star.classList.toggle('active', index < rating);
        });
    }

    setRating(rating) {
        if (this.options.readonly) return;

        this.rating = rating;
        this.highlightStars(rating);

        if (this.options.callback) {
            this.options.callback(rating);
        }

        // Trigger custom event
        const event = new CustomEvent('ratingChanged', {
            detail: { rating: rating }
        });
        this.container.dispatchEvent(event);
    }

    getRating() {
        return this.rating;
    }
}

// Form auto-save functionality
class FormAutoSave {
    constructor(form, options = {}) {
        this.form = form;
        this.options = {
            storageKey: options.storageKey || `autosave_${form.id || 'form'}`,
            saveInterval: options.saveInterval || 2000,
            excludeFields: options.excludeFields || ['password', 'password2']
        };

        this.init();
    }

    init() {
        // Load saved data
        this.loadSavedData();

        // Set up auto-save
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (!this.options.excludeFields.includes(input.name)) {
                input.addEventListener('input', debounce(() => this.saveData(), this.options.saveInterval));
            }
        });

        // Clear saved data on successful submission
        this.form.addEventListener('submit', () => {
            this.clearSavedData();
        });
    }

    saveData() {
        const formData = new FormData(this.form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            if (!this.options.excludeFields.includes(key)) {
                data[key] = value;
            }
        }

        setLocalStorage(this.options.storageKey, data);
    }

    loadSavedData() {
        const savedData = getLocalStorage(this.options.storageKey);
        if (savedData) {
            Object.keys(savedData).forEach(key => {
                const field = this.form.querySelector(`[name="${key}"]`);
                if (field && field.type !== 'file') {
                    field.value = savedData[key];
                }
            });
        }
    }

    clearSavedData() {
        try {
            localStorage.removeItem(this.options.storageKey);
        } catch (e) {
            console.warn('Could not clear saved data:', e);
        }
    }
}

function getEventStatus(scheduledAt, storedStatus) {
    if (storedStatus === 'cancelled' || storedStatus === 'completed') {
        return storedStatus;
    }

    const scheduledDate = new Date(scheduledAt);
    if (Number.isNaN(scheduledDate.getTime())) {
        return storedStatus || 'upcoming';
    }

    const now = new Date();
    const scheduledDay = scheduledDate.toDateString();
    const currentDay = now.toDateString();

    if (now > scheduledDate && currentDay !== scheduledDay) {
        return 'completed';
    }
    if (now >= scheduledDate) {
        return 'live';
    }
    return 'upcoming';
}

function refreshEventStatuses() {
    document.querySelectorAll('.js-event-status[data-scheduled-at]').forEach(statusElement => {
        const status = getEventStatus(statusElement.dataset.scheduledAt, statusElement.dataset.storedStatus);

        statusElement.classList.remove('status-upcoming', 'status-live', 'status-completed', 'status-cancelled');
        statusElement.classList.add(`status-${status}`);
        statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    refreshEventStatuses();
    if (document.querySelector('.js-event-status[data-scheduled-at]')) {
        setInterval(refreshEventStatuses, 5000);
    }
});

// Export functions for use in other scripts
window.showAlert = showAlert;
window.EventReviewPlatform = {
    showAlert,
    copyToClipboard,
    StarRating,
    FormAutoSave,
    refreshEventStatuses,
    formatDate,
    formatTime,
    debounce,
    throttle
};

// Password Visibility Toggle Init
function initializePasswordToggles() {
    document.querySelectorAll('.password-toggle-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const wrapper = this.closest('.input-icon-wrapper');
            if (!wrapper) return;
            const input = wrapper.querySelector('input');
            const icon = this.querySelector('i');
            if (!input) return;

            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
                this.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
                this.setAttribute('aria-label', 'Show password');
            }
        });
    });
}

// Login Form Handling & Validation
function initializeLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    const uInput = document.getElementById('username');
    const pInput = document.getElementById('password');
    const submitBtn = document.getElementById('loginSubmitBtn');

    loginForm.addEventListener('submit', function(e) {
        let valid = true;
        const uErr = document.getElementById('usernameError');
        const pErr = document.getElementById('passwordError');

        if (!uInput || !uInput.value.trim()) {
            valid = false;
            if (uInput) uInput.classList.add('is-invalid');
            if (uErr) uErr.textContent = 'Please enter your username';
        }

        if (!pInput || !pInput.value) {
            valid = false;
            if (pInput) pInput.classList.add('is-invalid');
            if (pErr) pErr.textContent = 'Please enter your password';
        }

        if (!valid) {
            e.preventDefault();
            return;
        }

        if (submitBtn) {
            const textSpan = submitBtn.querySelector('.btn-text');
            const spinnerSpan = submitBtn.querySelector('.btn-spinner');
            if (textSpan) textSpan.classList.add('d-none');
            if (spinnerSpan) spinnerSpan.classList.remove('d-none');
            submitBtn.disabled = true;
        }
    });
}

// Registration Form Live Validation & Availability Checks
function initializeRegistrationValidation() {
    const regForm = document.getElementById('registerForm');
    if (!regForm) return;

    const usernameInput = document.getElementById('reg_username');
    const emailInput = document.getElementById('reg_email');
    const fullNameInput = document.getElementById('reg_full_name');
    const passwordInput = document.getElementById('reg_password');
    const password2Input = document.getElementById('reg_password2');
    const termsCheck = document.getElementById('termsCheck');
    const submitBtn = document.getElementById('registerSubmitBtn');

    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    const ruleLength = document.getElementById('ruleLength');
    const ruleMatch = document.getElementById('ruleMatch');

    let usernameAvailable = false;
    let emailAvailable = false;

    function checkFormValidity() {
        const uVal = usernameInput ? usernameInput.value.trim() : '';
        const eVal = emailInput ? emailInput.value.trim() : '';
        const nVal = fullNameInput ? fullNameInput.value.trim() : '';
        const pVal = passwordInput ? passwordInput.value : '';
        const p2Val = password2Input ? password2Input.value : '';
        const isTerms = termsCheck ? termsCheck.checked : false;

        const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(eVal);
        const isPasswordMatch = pVal.length >= 6 && pVal === p2Val;

        const isValid = uVal.length >= 3 && usernameAvailable && isEmailValid && emailAvailable && nVal.length > 0 && isPasswordMatch && isTerms;
        if (submitBtn) {
            submitBtn.disabled = !isValid;
        }
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const val = this.value;
            let score = 0;

            if (val.length >= 6) score++;
            if (/[a-z]/.test(val) && /[A-Z]/.test(val)) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;

            if (ruleLength) {
                if (val.length >= 6) {
                    ruleLength.className = 'rule-item text-success fw-bold';
                    ruleLength.querySelector('i').className = 'fas fa-check-circle me-1';
                } else {
                    ruleLength.className = 'rule-item text-muted';
                    ruleLength.querySelector('i').className = 'fas fa-circle-notch me-1';
                }
            }

            if (strengthBar && strengthText) {
                if (val.length === 0) {
                    strengthBar.style.width = '0%';
                    strengthText.textContent = 'Not entered';
                    strengthText.className = 'text-muted';
                } else if (val.length < 6) {
                    strengthBar.style.width = '25%';
                    strengthBar.style.backgroundColor = '#ef4444';
                    strengthText.textContent = 'Weak (Too short)';
                    strengthText.className = 'text-danger';
                } else if (score <= 2) {
                    strengthBar.style.width = '55%';
                    strengthBar.style.backgroundColor = '#f59e0b';
                    strengthText.textContent = 'Medium';
                    strengthText.className = 'text-warning';
                } else {
                    strengthBar.style.width = '100%';
                    strengthBar.style.backgroundColor = '#10b981';
                    strengthText.textContent = 'Strong';
                    strengthText.className = 'text-success';
                }
            }

            if (password2Input && password2Input.value) {
                checkMatch();
            }
            checkFormValidity();
        });
    }

    function checkMatch() {
        if (!passwordInput || !password2Input) return;
        const p1 = passwordInput.value;
        const p2 = password2Input.value;
        const feedback = document.getElementById('password2Feedback');

        if (p2.length > 0 && p1 === p2) {
            password2Input.classList.remove('is-invalid');
            password2Input.classList.add('is-valid');
            if (feedback) feedback.innerHTML = '<span class="text-success"><i class="fas fa-check me-1"></i> Passwords match</span>';
            if (ruleMatch) {
                ruleMatch.className = 'rule-item text-success fw-bold';
                ruleMatch.querySelector('i').className = 'fas fa-check-circle me-1';
            }
        } else if (p2.length > 0) {
            password2Input.classList.remove('is-valid');
            password2Input.classList.add('is-invalid');
            if (feedback) feedback.innerHTML = '<span class="text-danger"><i class="fas fa-times me-1"></i> Passwords do not match</span>';
            if (ruleMatch) {
                ruleMatch.className = 'rule-item text-muted';
                ruleMatch.querySelector('i').className = 'fas fa-circle-notch me-1';
            }
        } else {
            password2Input.classList.remove('is-valid', 'is-invalid');
            if (feedback) feedback.innerHTML = '';
        }
    }

    if (password2Input) {
        password2Input.addEventListener('input', function() {
            checkMatch();
            checkFormValidity();
        });
    }

    let usernameTimeout;
    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            const val = this.value.trim();
            const feedback = document.getElementById('usernameFeedback');
            clearTimeout(usernameTimeout);

            if (val.length < 3) {
                usernameAvailable = false;
                usernameInput.classList.remove('is-valid');
                if (val.length > 0) {
                    usernameInput.classList.add('is-invalid');
                    if (feedback) feedback.innerHTML = '<span class="text-danger">Username must be at least 3 characters</span>';
                } else {
                    usernameInput.classList.remove('is-invalid');
                    if (feedback) feedback.innerHTML = '';
                }
                checkFormValidity();
                return;
            }

            usernameTimeout = setTimeout(() => {
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
                fetch('/api/check-username', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                    body: JSON.stringify({ username: val })
                })
                .then(res => res.json())
                .then(data => {
                    usernameAvailable = data.available;
                    if (data.available) {
                        usernameInput.classList.remove('is-invalid');
                        usernameInput.classList.add('is-valid');
                        if (feedback) feedback.innerHTML = '<span class="text-success"><i class="fas fa-check me-1"></i> Username available</span>';
                    } else {
                        usernameInput.classList.remove('is-valid');
                        usernameInput.classList.add('is-invalid');
                        if (feedback) feedback.innerHTML = '<span class="text-danger"><i class="fas fa-times me-1"></i> Username already taken</span>';
                    }
                    checkFormValidity();
                })
                .catch(() => {
                    usernameAvailable = true;
                    checkFormValidity();
                });
            }, 300);
        });
    }

    let emailTimeout;
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const val = this.value.trim();
            const feedback = document.getElementById('emailFeedback');
            clearTimeout(emailTimeout);

            const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
            if (!isEmailValid) {
                emailAvailable = false;
                emailInput.classList.remove('is-valid');
                if (val.length > 0) {
                    emailInput.classList.add('is-invalid');
                    if (feedback) feedback.innerHTML = '<span class="text-danger">Please enter a valid email address</span>';
                } else {
                    emailInput.classList.remove('is-invalid');
                    if (feedback) feedback.innerHTML = '';
                }
                checkFormValidity();
                return;
            }

            emailTimeout = setTimeout(() => {
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
                fetch('/api/check-user-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                    body: JSON.stringify({ email: val })
                })
                .then(res => res.json())
                .then(data => {
                    emailAvailable = data.available;
                    if (data.available) {
                        emailInput.classList.remove('is-invalid');
                        emailInput.classList.add('is-valid');
                        if (feedback) feedback.innerHTML = '<span class="text-success"><i class="fas fa-check me-1"></i> Email available</span>';
                    } else {
                        emailInput.classList.remove('is-valid');
                        emailInput.classList.add('is-invalid');
                        if (feedback) feedback.innerHTML = '<span class="text-danger"><i class="fas fa-times me-1"></i> Email already registered</span>';
                    }
                    checkFormValidity();
                })
                .catch(() => {
                    emailAvailable = true;
                    checkFormValidity();
                });
            }, 300);
        });
    }

    if (fullNameInput) fullNameInput.addEventListener('input', checkFormValidity);
    if (termsCheck) termsCheck.addEventListener('change', checkFormValidity);

    regForm.addEventListener('submit', function(e) {
        if (submitBtn) {
            const textSpan = submitBtn.querySelector('.btn-text');
            const spinnerSpan = submitBtn.querySelector('.btn-spinner');
            if (textSpan) textSpan.classList.add('d-none');
            if (spinnerSpan) spinnerSpan.classList.remove('d-none');
            submitBtn.disabled = true;
        }
    });
}

