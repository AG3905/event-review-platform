// Main JavaScript functionality for Event Review Platform

document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeAlerts();
    initializeFormValidation();
    initializeAnimations();
});

// Navigation functionality
function initializeNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');

            // Animate hamburger bars
            const bars = navToggle.querySelectorAll('.bar');
            bars.forEach((bar, index) => {
                bar.style.transform = navMenu.classList.contains('active') 
                    ? `rotate(${index === 0 ? 45 : index === 2 ? -45 : 0}deg) translate(${index === 1 ? '100px' : '0'}, ${index === 0 ? '6px' : index === 2 ? '-6px' : '0'})`
                    : 'none';
                bar.style.opacity = navMenu.classList.contains('active') && index === 1 ? '0' : '1';
            });
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
        });
    }
}

// Alert system
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }

        // Auto-hide alerts after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
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
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        setTimeout(() => alert.remove(), 300);
    });

    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
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

    // Password strength indicator
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        if (field.name === 'password') {
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
        strengthDiv.innerHTML = `
            <div class="strength-bar">
                <div class="strength-fill" style="width: ${(strength / 5) * 100}%; background-color: ${color};"></div>
            </div>
            <span class="strength-text" style="color: ${color};">${message}</span>
        `;
        strengthDiv.style.display = 'block';
    } else {
        strengthDiv.style.display = 'none';
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
    const animatedElements = document.querySelectorAll('.feature-card, .stat-card, .event-card, .review-card');
    animatedElements.forEach(el => observer.observe(el));

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

// Export functions for use in other scripts
window.EventReviewPlatform = {
    showAlert,
    copyToClipboard,
    StarRating,
    FormAutoSave,
    formatDate,
    formatTime,
    debounce,
    throttle
};
