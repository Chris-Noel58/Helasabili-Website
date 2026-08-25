// ========================================
// Main JavaScript for NCHSM Website
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initScrollToTop();
    initAnimations();
    initFormValidation();
    initNavbar();
    initTypingAnimation();
    initHeroSlideshow();
});

// ========================================
// Scroll to Top Button
// ========================================

function initScrollToTop() {
    const scrollBtn = document.getElementById('scrollTopBtn');
    
    if (!scrollBtn) return;
    
    // Show button when scrolled down
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.add('show');
        } else {
            scrollBtn.classList.remove('show');
        }
    });
    
    // Smooth scroll on click
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ========================================
// Animations
// ========================================

function initAnimations() {
    // Animated counter for statistics
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length > 0) {
        observeElements(counters, animateCounter);
    }
    
    // Fade in elements on scroll
    const fadeElements = document.querySelectorAll('[data-fade-in]');
    if (fadeElements.length > 0) {
        observeElements(fadeElements, function(el) {
            el.classList.add('animate-fade-in');
        });
    }
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-counter'));
    const duration = 2000; // 2 seconds
    const start = 0;
    const startTime = Date.now();
    
    function updateCounter() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(start + (target - start) * progress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    updateCounter();
}

function observeElements(elements, callback) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                callback(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => observer.observe(el));
}

// ========================================
// Form Validation
// ========================================

function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// ========================================
// Navbar
// ========================================

function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    if (!navbar) return;
    
    // Add shadow on scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 50) {
            navbar.classList.add('shadow-sm');
        } else {
            navbar.classList.remove('shadow-sm');
        }
    });
}

// ========================================
// Image Lazy Loading
// ========================================

function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// ========================================
// Typing Animation
// ========================================

function initTypingAnimation() {
    try {
        const phrases = [
            'This is where the future is built.',
            'Learn. Lead. Heal.',
            'Join a community shaping healthcare leaders.'
        ];

        // Try multiple selectors so we work even if hero markup changes
        let el = document.querySelector('.hero .typed-text') || document.querySelector('.typed-text');

        // If not found, try to create the typed element below the main hero heading
        if (!el) {
            const hero = document.querySelector('.hero') || document.querySelector('.hero-section') || document.querySelector('.jumbotron');
            if (hero) {
                const heading = hero.querySelector('h1') || hero.querySelector('.display-1') || hero.querySelector('h2');
                if (heading) {
                    const container = document.createElement('div');
                    container.className = 'typed-container';
                    const span = document.createElement('span');
                    span.className = 'typed-text';
                    container.appendChild(span);
                    heading.insertAdjacentElement('afterend', container);
                    el = span;
                }
            }
        }

        if (!el) return;

        // Avoid adding multiple cursors
        let cursor = el.parentNode.querySelector('.typed-cursor');
        if (!cursor) {
            cursor = document.createElement('span');
            cursor.className = 'typed-cursor';
            el.parentNode.appendChild(cursor);
        }

        let phraseIndex = 0;
        let letterIndex = 0;
        let typing = true;
        let isRunning = true;

        function type() {
            if (!isRunning) return;
            const current = phrases[phraseIndex];
            if (typing) {
                el.textContent = current.slice(0, letterIndex + 1);
                letterIndex++;
                if (letterIndex === current.length) {
                    typing = false;
                    setTimeout(type, 1500);
                } else {
                    setTimeout(type, 80 + Math.random() * 80);
                }
            } else {
                el.textContent = current.slice(0, letterIndex - 1);
                letterIndex--;
                if (letterIndex === 0) {
                    typing = true;
                    phraseIndex = (phraseIndex + 1) % phrases.length;
                    setTimeout(type, 500);
                } else {
                    setTimeout(type, 40);
                }
            }
        }

        // Start typing after a short delay to ensure element is visible
        setTimeout(type, 200);

        // Pause/resume on visibility change to save CPU
        document.addEventListener('visibilitychange', function() {
            isRunning = !document.hidden;
        });
    } catch (err) {
        // Fail silently to avoid breaking other scripts
        console.error('Typing animation error:', err);
    }
}

// ========================================
// Hero background slideshow (robust with DOM fallback)
// ========================================
function initHeroSlideshow() {
    try {
        const hero = document.querySelector('.hero');
        if (!hero) return;

        // read images from data attribute (JSON array) or fallback to empty
        let images = [];
        try {
            const raw = hero.getAttribute('data-bg-images');
            images = raw ? JSON.parse(raw) : [];
        } catch (e) {
            images = [];
        }

        // If no images from data attribute, try to collect from gallery section in the page
        if (!images.length) {
            const galleryImgs = Array.from(document.querySelectorAll('.gallery-item img, .gallery img, .gallery-image img'))
                .map(img => img.dataset.src || img.getAttribute('src'))
                .filter(Boolean);
            // remove duplicates and limit to 8
            images = [...new Set(galleryImgs)].slice(0, 8);
        }

        if (!images.length) return;

        const layers = Array.from(hero.querySelectorAll('.hero-bg-layer'));
        if (layers.length < 2) return;

        // preload images
        images.forEach(src => { const img = new Image(); img.src = src; });

        let current = 0;
        const interval = parseInt(hero.getAttribute('data-bg-interval')) || 6000;

        // initialize first layer
        layers.forEach((layer, i) => {
            layer.style.backgroundImage = `url('${images[i % images.length]}')`;
            layer.classList.toggle('visible', i === 0);
        });

        setInterval(() => {
            const nextIndex = (current + 1) % images.length;
            const topLayerIndex = (current + 1) % layers.length;
            const topLayer = layers[topLayerIndex];

            topLayer.style.backgroundImage = `url('${images[nextIndex]}')`;

            // set visible only for the top layer
            layers.forEach((l, idx) => l.classList.toggle('visible', idx === topLayerIndex));

            current = nextIndex;
        }, interval);
    } catch (err) {
        console.error('Hero slideshow error:', err);
    }
}

// ========================================
// Utility Functions
// ========================================

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES'
    }).format(value);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-KE', options);
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.alert-container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Debounce function
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// ========================================
// API Helpers
// ========================================

// Fetch with CSRF token
async function fetchWithCSRF(url, options = {}) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (csrftoken && options.method && options.method.toUpperCase() !== 'GET') {
        headers['X-CSRFToken'] = csrftoken;
    }
    
    return fetch(url, {
        ...options,
        headers
    });
}

// ========================================
// Export Functions
// ========================================

window.NCHSM = {
    formatCurrency,
    formatDate,
    showNotification,
    debounce,
    fetchWithCSRF
};
