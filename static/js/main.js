// Back to top button
const backToTopButton = document.createElement('a');
backToTopButton.href = '#';
backToTopButton.className = 'back-to-top';
backToTopButton.innerHTML = '&uarr;';
backToTopButton.title = 'Back to top';
document.body.appendChild(backToTopButton);

// Show/hide back to top button
window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
        backToTopButton.classList.add('visible');
    } else {
        backToTopButton.classList.remove('visible');
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 70, // Adjust for fixed header
                behavior: 'smooth'
            });
        }
    });
});

// Add animation to elements when they come into view
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (elementPosition < screenPosition) {
            element.classList.add('animate-fade-in');
        }
    });
};

// Initialize animations
window.addEventListener('load', () => {
    // Add animation class to elements that should animate on load
    document.querySelectorAll('.hero-section, .card, section').forEach((el, index) => {
        el.style.opacity = '0';
        el.classList.add('animate-on-scroll');
    });
    
    // Trigger initial animation check
    animateOnScroll();
});

// Check for animations on scroll
window.addEventListener('scroll', animateOnScroll);

// Initialize tooltips
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Form validation
const forms = document.querySelectorAll('.needs-validation');
Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    }, false);
});

// Add active class to current nav link
const currentLocation = location.href;
const menuItems = document.querySelectorAll('.nav-link');
const menuLength = menuItems.length;

for (let i = 0; i < menuLength; i++) {
    if (menuItems[i].href === currentLocation) {
        menuItems[i].classList.add('active');
    }
}

// Image lazy loading
if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading is supported
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => {
        img.src = img.dataset.src;
    });
} else {
    // Fallback for browsers that don't support lazy loading
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
    document.body.appendChild(script);
}

// Add animation to dropdown menus
const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
dropdownElementList.map(function (dropdownToggleEl) {
    return new bootstrap.Dropdown(dropdownToggleEl, {
        popperConfig: (defaultBsPopperConfig) => ({
            ...defaultBsPopperConfig,
            placement: 'bottom-start',
        })
    });
});
