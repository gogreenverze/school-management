// Custom JavaScript for School Management System

/**
 * Toast notification system
 */
class ToastNotification {
    constructor() {
        this.toastContainer = null;
        this.createToastContainer();
    }

    createToastContainer() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';
            this.toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            this.toastContainer.style.zIndex = '1090';
            document.body.appendChild(this.toastContainer);
        } else {
            this.toastContainer = document.getElementById('toast-container');
        }
    }

    show(message, type = 'info', duration = 3000) {
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center border-0 fade hide`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        // Set background color based on type
        let bgColor, iconClass;
        switch (type) {
            case 'success':
                bgColor = 'bg-success';
                iconClass = 'fas fa-check-circle';
                break;
            case 'warning':
                bgColor = 'bg-warning';
                iconClass = 'fas fa-exclamation-triangle';
                break;
            case 'error':
                bgColor = 'bg-danger';
                iconClass = 'fas fa-times-circle';
                break;
            default:
                bgColor = 'bg-info';
                iconClass = 'fas fa-info-circle';
        }

        // Create toast content
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body ${bgColor} text-white">
                    <i class="${iconClass} me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        // Add toast to container
        this.toastContainer.appendChild(toast);

        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, {
            animation: true,
            autohide: true,
            delay: duration
        });

        bsToast.show();

        // Remove toast from DOM after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

// Create global toast instance
const toast = new ToastNotification();

/**
 * Page transition effects - DISABLED to improve performance
 *
 * The pink overlay animation was removed as it was slowing down the app.
 */

/**
 * Initialize on DOM content loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Page transitions have been disabled to improve performance

    // Remove any existing page transition overlays and styles
    const existingOverlay = document.getElementById('page-transition-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    // Remove any existing page transition styles
    const existingStyle = document.getElementById('page-transition-style');
    if (existingStyle) {
        existingStyle.remove();
    }

    // Mobile menu toggle with animation
    const menuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');

    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            mobileMenu.classList.toggle('show');

            // Change icon based on menu state with animation
            const icon = menuToggle.querySelector('i');
            if (mobileMenu.classList.contains('show')) {
                icon.style.transition = 'transform 0.3s ease';
                icon.style.transform = 'rotate(90deg)';
                setTimeout(() => {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                    icon.style.transform = 'rotate(0deg)';
                }, 150);
            } else {
                icon.style.transition = 'transform 0.3s ease';
                icon.style.transform = 'rotate(90deg)';
                setTimeout(() => {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                    icon.style.transform = 'rotate(0deg)';
                }, 150);
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuToggle.contains(event.target) && !mobileMenu.contains(event.target) && mobileMenu.classList.contains('show')) {
                mobileMenu.classList.remove('show');
                const icon = menuToggle.querySelector('i');
                icon.style.transition = 'transform 0.3s ease';
                icon.style.transform = 'rotate(90deg)';
                setTimeout(() => {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                    icon.style.transform = 'rotate(0deg)';
                }, 150);
            }
        });
    }

    // Convert traditional alerts to toast notifications
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        let type = 'info';
        if (alert.classList.contains('alert-success')) type = 'success';
        if (alert.classList.contains('alert-warning')) type = 'warning';
        if (alert.classList.contains('alert-danger')) type = 'error';

        const message = alert.innerText;

        // Hide the original alert
        alert.style.display = 'none';

        // Show toast notification
        setTimeout(() => {
            toast.show(message, type);
        }, 500);
    });

    // Initialize tooltips with animation
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            animation: true,
            delay: { show: 100, hide: 100 }
        });
    });

    // Initialize popovers with animation
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            animation: true,
            trigger: 'hover focus'
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const x = e.clientX - e.target.getBoundingClientRect().left;
            const y = e.clientY - e.target.getBoundingClientRect().top;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add ripple effect style
    if (!document.getElementById('ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            .btn {
                position: relative;
                overflow: hidden;
            }
            .ripple-effect {
                position: absolute;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.4);
                width: 100px;
                height: 100px;
                margin-top: -50px;
                margin-left: -50px;
                animation: ripple 0.6s linear;
                transform: scale(0);
                opacity: 1;
                pointer-events: none;
            }
            @keyframes ripple {
                to {
                    transform: scale(3);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
});

/**
 * Enhanced form validation with visual feedback
 */
class FormValidator {
    constructor() {
        this.init();
    }

    init() {
        // Fetch all forms we want to apply custom validation styles to
        const forms = document.querySelectorAll('.needs-validation');

        // Loop over them and prevent submission
        Array.from(forms).forEach(form => {
            // Add floating labels to form inputs
            this.addFloatingLabels(form);

            // Add input animations
            this.addInputAnimations(form);

            // Handle form submission
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();

                    // Show toast notification for validation errors
                    toast.show('Please check the form for errors', 'error');

                    // Highlight first invalid field
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });

                        // Add shake animation to invalid fields
                        const invalidFields = form.querySelectorAll(':invalid');
                        invalidFields.forEach(field => {
                            field.classList.add('shake-animation');
                            setTimeout(() => {
                                field.classList.remove('shake-animation');
                            }, 600);
                        });
                    }
                } else {
                    // Show loading state on submit button
                    const submitBtn = form.querySelector('[type="submit"]');
                    if (submitBtn) {
                        const originalText = submitBtn.innerHTML;
                        submitBtn.disabled = true;
                        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Processing...';

                        // Restore button after 2 seconds if form is not actually submitted
                        // (this is just for demo purposes, in a real app this would be handled by the server response)
                        setTimeout(() => {
                            if (submitBtn.disabled) {
                                submitBtn.disabled = false;
                                submitBtn.innerHTML = originalText;
                            }
                        }, 2000);
                    }
                }

                form.classList.add('was-validated');
            }, false);

            // Real-time validation feedback
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    if (input.checkValidity()) {
                        input.classList.add('is-valid');
                        input.classList.remove('is-invalid');
                    } else if (input.value !== '') {
                        input.classList.add('is-invalid');
                        input.classList.remove('is-valid');
                    }
                });
            });
        });

        // Add shake animation style
        if (!document.getElementById('shake-animation-style')) {
            const style = document.createElement('style');
            style.id = 'shake-animation-style';
            style.textContent = `
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                    20%, 40%, 60%, 80% { transform: translateX(5px); }
                }
                .shake-animation {
                    animation: shake 0.6s cubic-bezier(.36,.07,.19,.97) both;
                    transform: translate3d(0, 0, 0);
                    backface-visibility: hidden;
                    perspective: 1000px;
                }
            `;
            document.head.appendChild(style);
        }
    }

    addFloatingLabels(form) {
        const inputs = form.querySelectorAll('.form-control:not(.floating-applied)');
        inputs.forEach(input => {
            const parent = input.parentElement;
            const label = parent.querySelector('label[for="' + input.id + '"]');

            if (label && !parent.classList.contains('form-floating')) {
                // Skip if already in a floating label container
                if (!parent.closest('.form-floating')) {
                    // Create floating label structure
                    const floatingDiv = document.createElement('div');
                    floatingDiv.className = 'form-floating mb-3';

                    // Move input into floating div
                    parent.insertBefore(floatingDiv, input);
                    floatingDiv.appendChild(input);
                    floatingDiv.appendChild(label);

                    // Add placeholder if not present
                    if (!input.placeholder) {
                        input.placeholder = label.textContent;
                    }

                    // Mark as processed
                    input.classList.add('floating-applied');
                }
            }
        });
    }

    addInputAnimations(form) {
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            // Focus effect
            input.addEventListener('focus', () => {
                input.style.transition = 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)';
                input.style.transform = 'translateY(-2px)';
                input.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
            });

            // Blur effect
            input.addEventListener('blur', () => {
                input.style.transform = 'translateY(0)';
                input.style.boxShadow = '';
            });
        });
    }
}

// Initialize form validator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new FormValidator();

    // Mobile navigation active state with animation
    const currentPath = window.location.pathname;
    const mobileNavItems = document.querySelectorAll('.mobile-nav-item');

    mobileNavItems.forEach(function(item, index) {
        const href = item.getAttribute('href');
        if (href && currentPath.startsWith(href)) {
            // Add active class with delay for animation
            setTimeout(() => {
                item.classList.add('active');

                // Add bounce animation to icon
                const icon = item.querySelector('i');
                if (icon) {
                    icon.style.animation = 'bounce 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                }
            }, 100 * index);
        }
    });
});
