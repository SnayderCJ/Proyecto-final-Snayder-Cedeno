document.addEventListener("DOMContentLoaded", function () {
    // Password strength meter
    const passwordInput = document.querySelector('input[name="password1"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', function(e) {
            const password = e.target.value;
            const strength = calculatePasswordStrength(password);
            const strengthBar = document.getElementById('strengthBar');
            const strengthText = document.getElementById('strengthText');
            
            // Update strength bar
            strengthBar.style.width = strength.score + '%';
            
            // Update colors based on strength
            if (strength.score < 25) {
                strengthBar.className = 'h-full bg-destructive transition-all duration-300 rounded-full';
                strengthText.className = 'text-xs font-medium text-destructive';
                strengthText.textContent = 'Muy débil';
            } else if (strength.score < 50) {
                strengthBar.className = 'h-full bg-warning transition-all duration-300 rounded-full';
                strengthText.className = 'text-xs font-medium text-warning';
                strengthText.textContent = 'Débil';
            } else if (strength.score < 75) {
                strengthBar.className = 'h-full bg-primary transition-all duration-300 rounded-full';
                strengthText.className = 'text-xs font-medium text-primary';
                strengthText.textContent = 'Media';
            } else {
                strengthBar.className = 'h-full bg-success transition-all duration-300 rounded-full';
                strengthText.className = 'text-xs font-medium text-success';
                strengthText.textContent = 'Fuerte';
            }
        });
    }

    function calculatePasswordStrength(password) {
        let score = 0;
        
        // Length
        if (password.length > 6) score += 20;
        if (password.length > 8) score += 10;
        if (password.length > 12) score += 10;
        
        // Complexity
        if (/[A-Z]/.test(password)) score += 15; // Uppercase
        if (/[a-z]/.test(password)) score += 15; // Lowercase
        if (/[0-9]/.test(password)) score += 15; // Numbers
        if (/[^A-Za-z0-9]/.test(password)) score += 15; // Special chars
        
        // Variety
        const uniqueChars = new Set(password).size;
        score += Math.min(uniqueChars * 2, 15); // Up to 15 points for variety
        
        return {
            score: Math.min(score, 100) // Cap at 100%
        };
    }

    // Toast notifications logic
    const toasts = document.querySelectorAll(".custom-toast");

    toasts.forEach(toast => {
        let isManuallyClose = false;
        let autoCloseTimer;
        
        // Función para cerrar el toast
        const closeToast = () => {
            if (toast && toast.parentNode) {
                toast.style.opacity = "0";
                toast.style.transition = "opacity 0.5s ease";
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 500);
            }
        };

        // Auto-cerrar después de 5 segundos
        autoCloseTimer = setTimeout(() => {
            if (!isManuallyClose) {
                closeToast();
            }
        }, 5000);

        // Manejar el botón de cerrar manualmente
        const closeButton = toast.querySelector('.close-toast');
        if (closeButton) {
            closeButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                isManuallyClose = true;
                clearTimeout(autoCloseTimer);
                closeToast();
            });
        }

        // Pausar auto-close al hacer hover
        toast.addEventListener('mouseenter', () => {
            clearTimeout(autoCloseTimer);
        });

        // Reanudar al quitar el hover (solo si no se cerró manualmente)
        toast.addEventListener('mouseleave', () => {
            if (!isManuallyClose) {
                autoCloseTimer = setTimeout(() => {
                    if (!isManuallyClose) {
                        closeToast();
                    }
                }, 2000);
            }
        });
    });

    // Form transition logic
    const loginLink = document.querySelector('a[href*="login"]');
    const registerLink = document.querySelector('a[href*="register"]');
    const formContainer = document.querySelector('form').parentElement;

    function animateFormTransition(e) {
        e.preventDefault();
        const href = e.currentTarget.getAttribute('href');
        
        // Animate form out
        formContainer.style.transform = 'translateY(-20px)';
        formContainer.style.opacity = '0';
        
        setTimeout(() => {
            window.location.href = href;
        }, 300);
    }

    if (loginLink) {
        loginLink.addEventListener('click', animateFormTransition);
    }
    if (registerLink) {
        registerLink.addEventListener('click', animateFormTransition);
    }

    // Animate form in on page load
    formContainer.style.opacity = '0';
    formContainer.style.transform = 'translateY(20px)';
    formContainer.style.transition = 'all 0.5s ease';
    
    requestAnimationFrame(() => {
        formContainer.style.opacity = '1';
        formContainer.style.transform = 'translateY(0)';
    });
});
