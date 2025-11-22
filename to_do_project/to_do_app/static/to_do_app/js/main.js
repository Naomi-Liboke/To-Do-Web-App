// JavaScript for Django To-Do App

document.addEventListener('DOMContentLoaded', function() {
    console.log('Django To-Do App JavaScript loaded');

    // Initialize theme system first - with improved reliability
    initializeTheme();

    // Rest of your existing code remains the same...
    // Mark task as completed/pending (frontend only - for visual feedback)
    const completeButtons = document.querySelectorAll('.complete-btn');
    completeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // This is just for visual feedback - the actual toggle happens via form submission
            const taskItem = this.closest('.task-item');
            const isCompleted = taskItem.classList.contains('task-completed');
            
            if (isCompleted) {
                taskItem.classList.remove('task-completed');
            } else {
                taskItem.classList.add('task-completed');
            }
        });
    });

    // Delete task confirmation
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            let firstInvalidField = null;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'var(--danger-color)';
                    field.style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue('--background-color');
                    
                    // Add shake animation
                    field.classList.add('shake');
                    setTimeout(() => {
                        field.classList.remove('shake');
                    }, 500);
                    
                    if (!firstInvalidField) {
                        firstInvalidField = field;
                    }
                } else {
                    field.style.borderColor = '';
                    field.style.backgroundColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first invalid field
                if (firstInvalidField) {
                    firstInvalidField.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                    firstInvalidField.focus();
                }
                
                // Show error message
                showMessage('Please fill in all required fields.', 'error');
            }
        });
    });

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 300);
        }, 5000);
    });

    // Category color coding
    function updateCategoryColors() {
        const categoryBadges = document.querySelectorAll('.category-badge');
        categoryBadges.forEach(badge => {
            const category = badge.textContent.toLowerCase().trim();
            badge.className = 'category-badge'; // Reset classes
            
            if (category.includes('work')) {
                badge.classList.add('category-work');
            } else if (category.includes('school') || category.includes('education')) {
                badge.classList.add('category-school');
            } else if (category.includes('personal') || category.includes('home')) {
                badge.classList.add('category-personal');
            } else {
                // Default category
                badge.classList.add('category-work');
            }
        });
    }

    // Initialize category colors
    updateCategoryColors();

    // Task search functionality
    const searchInput = document.querySelector('#task-search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const taskItems = document.querySelectorAll('.task-item');
            
            taskItems.forEach(item => {
                const taskTitle = item.querySelector('.task-title').textContent.toLowerCase();
                const taskDescription = item.querySelector('.task-meta') ? item.querySelector('.task-meta').textContent.toLowerCase() : '';
                
                if (taskTitle.includes(searchTerm) || taskDescription.includes(searchTerm)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // Task filter by category
    const categoryFilter = document.querySelector('#category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function(e) {
            const selectedCategory = e.target.value;
            const taskItems = document.querySelectorAll('.task-item');
            
            taskItems.forEach(item => {
                const categoryBadge = item.querySelector('.category-badge');
                if (categoryBadge) {
                    const taskCategory = categoryBadge.textContent.toLowerCase().trim();
                    
                    if (selectedCategory === '' || taskCategory.includes(selectedCategory.toLowerCase())) {
                        item.style.display = 'flex';
                    } else {
                        item.style.display = 'none';
                    }
                }
            });
        });
    }

    // Progress bar animation
    function animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width || bar.getAttribute('data-width');
            if (width) {
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
            }
        });
    }

    // Initialize progress bar animations
    animateProgressBars();

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.style.fontSize = '0.875rem';
            counter.style.color = 'var(--text-light)';
            counter.style.textAlign = 'right';
            counter.style.marginTop = '0.5rem';
            
            textarea.parentNode.appendChild(counter);
            
            function updateCounter() {
                const currentLength = textarea.value.length;
                counter.textContent = `${currentLength}/${maxLength}`;
                
                if (currentLength > maxLength * 0.9) {
                    counter.style.color = 'var(--warning-color)';
                } else if (currentLength > maxLength) {
                    counter.style.color = 'var(--danger-color)';
                } else {
                    counter.style.color = 'var(--text-light)';
                }
            }
            
            textarea.addEventListener('input', updateCounter);
            updateCounter(); // Initial update
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Welcome message animation
    const welcome = document.getElementById('welcome-message');
    if (welcome) {
        // Fade in after 0.5s
        setTimeout(() => {
            welcome.classList.add('show');
        }, 500);

        // Fade out after 4s
        setTimeout(() => {
            welcome.classList.remove('show');
            // Remove from DOM after animation
            setTimeout(() => {
                if (welcome.parentElement) {
                    welcome.remove();
                }
            }, 1000);
        }, 4500);
    }

    console.log('All JavaScript features initialized');
});

// IMPROVED Theme initialization function
function initializeTheme() {
    console.log('Initializing theme system...');
    
    // Apply theme immediately based on saved preference or system preference
    applyStoredTheme();
    
    // Set up theme toggle with event delegation for better reliability
    document.addEventListener('click', function(e) {
        if (e.target.closest('.theme-toggle')) {
            toggleTheme();
        }
    });
    
    // Also set up direct event listener for immediate response
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        console.log('Theme toggle button found, setting up direct listener');
        themeToggle.addEventListener('click', toggleTheme);
    } else {
        console.log('Theme toggle button not found on initial load');
        // Try again after a short delay in case the button loads later
        setTimeout(() => {
            const retryToggle = document.querySelector('.theme-toggle');
            if (retryToggle) {
                console.log('Theme toggle button found on retry');
                retryToggle.addEventListener('click', toggleTheme);
                updateThemeIcon(); // Ensure icon is correct
            }
        }, 100);
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        // Only apply system theme if no manual preference is stored
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            updateThemeIcon();
        }
    });
}

// Separate function to apply stored theme
function applyStoredTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    let themeToApply;
    
    if (savedTheme) {
        themeToApply = savedTheme;
        console.log('Using saved theme:', savedTheme);
    } else if (prefersDark) {
        themeToApply = 'dark';
        console.log('Using system dark theme preference');
    } else {
        themeToApply = 'light';
        console.log('Using default light theme');
    }
    
    document.documentElement.setAttribute('data-theme', themeToApply);
    updateThemeIcon();
}

// Separate function to toggle theme
function toggleTheme() {
    console.log('Theme toggle clicked');
    const htmlElement = document.documentElement;
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    console.log('Switching theme from', currentTheme, 'to', newTheme);
    
    // Apply new theme
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update button icon with animation
    updateThemeIcon();
    
    // Add visual feedback
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.style.transform = 'scale(0.8)';
        setTimeout(() => {
            themeToggle.style.transform = 'scale(1)';
        }, 150);
    }
}

// Separate function to update theme icon
function updateThemeIcon() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) {
        console.log('Theme toggle button not found for icon update');
        return;
    }
    
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newIcon = currentTheme === 'dark' ? '☀️' : '🌙';
    
    console.log('Updating theme icon to:', newIcon);
    themeToggle.innerHTML = newIcon;
}

// Helper function to show messages
function showMessage(text, type = 'info') {
    // Remove existing custom messages
    const existingMessages = document.querySelectorAll('.custom-message');
    existingMessages.forEach(msg => {
        if (msg.parentElement) {
            msg.remove();
        }
    });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message custom-message ${type}`;
    messageDiv.textContent = text;
    messageDiv.style.marginBottom = '1rem';
    
    const mainContent = document.querySelector('main .container');
    if (mainContent) {
        mainContent.insertBefore(messageDiv, mainContent.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (messageDiv.parentElement) {
                    messageDiv.remove();
                }
            }, 300);
        }, 5000);
    }
}

// Add shake animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    .shake {
        animation: shake 0.5s ease-in-out;
    }
    .progress-bar {
        transition: width 1s ease-in-out;
    }
    
    /* Theme toggle animation */
    .theme-toggle {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);

// Utility function for making AJAX requests (if needed later)
function makeRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Request failed:', error);
        throw error;
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Debug function to check theme status
function debugTheme() {
    console.log('Current theme:', document.documentElement.getAttribute('data-theme'));
    console.log('Saved theme:', localStorage.getItem('theme'));
    console.log('System prefers dark:', window.matchMedia('(prefers-color-scheme: dark)').matches);
    console.log('Theme toggle found:', document.querySelector('.theme-toggle') !== null);
}

// Make debug function available globally for testing
window.debugTheme = debugTheme;

