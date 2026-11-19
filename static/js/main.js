/* Helasabili public site: small, dependency-free UI behaviour. Loaded with `defer`. */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ---------- Mobile navigation ---------- */
    function initNav() {
        var nav = document.getElementById('siteNav');
        var openBtn = document.querySelector('[data-nav-open]');
        var backdrop = document.querySelector('.nav-backdrop');
        if (!nav || !openBtn) return;

        function setOpen(open) {
            document.body.classList.toggle('nav-open', open);
            openBtn.setAttribute('aria-expanded', String(open));
            openBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
            if (backdrop) backdrop.hidden = !open;
            if (open) {
                var first = nav.querySelector('a');
                if (first) first.focus({ preventScroll: true });
            }
        }

        openBtn.addEventListener('click', function () {
            setOpen(!document.body.classList.contains('nav-open'));
        });
        document.querySelectorAll('[data-nav-close]').forEach(function (el) {
            el.addEventListener('click', function () { setOpen(false); openBtn.focus(); });
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && document.body.classList.contains('nav-open')) {
                setOpen(false);
                openBtn.focus();
            }
        });
        window.matchMedia('(min-width: 1100px)').addEventListener('change', function (e) {
            if (e.matches) setOpen(false);
        });
    }

    /* ---------- Header shadow once the page scrolls ---------- */
    function initHeader() {
        var header = document.getElementById('siteHeader');
        if (!header || !('IntersectionObserver' in window)) return;
        var sentinel = document.createElement('div');
        sentinel.setAttribute('aria-hidden', 'true');
        sentinel.style.cssText = 'position:absolute;top:0;height:1px;width:1px;';
        document.body.prepend(sentinel);
        new IntersectionObserver(function (entries) {
            header.classList.toggle('is-scrolled', !entries[0].isIntersecting);
        }).observe(sentinel);
    }

    /* ---------- Featured listings showcase (hero) ----------
       A native scroll-snap track (free swiping on phones). The green progress bar on the
       active dot is a CSS animation; when it ends we advance, so pausing the animation
       pauses autoplay and the two can never drift apart. */
    function initShowcase() {
        var root = document.querySelector('[data-showcase]');
        if (!root) return;
        var track = root.querySelector('.showcase__track');
        var slides = Array.prototype.slice.call(track.children);
        var dots = Array.prototype.slice.call(root.querySelectorAll('[data-showcase-dot]'));
        var caption = root.querySelector('[data-showcase-caption]');
        var ambient = document.querySelector('[data-ambient]');
        var counter = root.querySelector('[data-showcase-current]');
        var index = 0;
        if (slides.length < 2) return;

        root.style.setProperty('--showcase-interval', (parseInt(root.dataset.interval, 10) || 5500) + 'ms');
        if (reduceMotion) root.classList.add('is-paused');

        function setActive(i) {
            if (i === index || i < 0 || i >= slides.length) return;
            index = i;
            dots.forEach(function (dot, k) {
                dot.classList.toggle('is-active', k === i);
                dot.setAttribute('aria-selected', String(k === i));
            });
            if (counter) counter.textContent = String(i + 1);
            var title = slides[i].dataset.caption || '';
            if (caption) {
                caption.classList.add('is-changing');
                setTimeout(function () { caption.textContent = title; caption.classList.remove('is-changing'); }, 200);
            }
            if (ambient && !ambient.hasAttribute('data-ambient-locked') && slides[i].dataset.ambientSrc) {
                ambient.classList.add('is-fading');
                setTimeout(function () {
                    ambient.onload = function () { ambient.classList.remove('is-fading'); };
                    ambient.src = slides[i].dataset.ambientSrc;
                }, 350);
            }
        }

        function goTo(i) {
            i = (i + slides.length) % slides.length;
            track.scrollTo({ left: slides[i].offsetLeft - slides[0].offsetLeft, behavior: reduceMotion ? 'auto' : 'smooth' });
            setActive(i);
        }

        // Keep dots in sync with manual swipes.
        var raf = null;
        track.addEventListener('scroll', function () {
            if (raf) return;
            raf = requestAnimationFrame(function () {
                raf = null;
                setActive(Math.round(track.scrollLeft / track.clientWidth));
            });
        }, { passive: true });

        // Autoplay: advance when the active dot's progress animation finishes.
        root.addEventListener('animationend', function (e) {
            if (e.target.closest('.showcase__dot.is-active')) goTo(index + 1);
        });

        dots.forEach(function (dot) {
            dot.addEventListener('click', function () { goTo(parseInt(dot.dataset.showcaseDot, 10)); });
        });
        var prev = root.querySelector('[data-showcase-prev]');
        var next = root.querySelector('[data-showcase-next]');
        if (prev) prev.addEventListener('click', function () { goTo(index - 1); });
        if (next) next.addEventListener('click', function () { goTo(index + 1); });
        track.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(index - 1); }
            if (e.key === 'ArrowRight') { e.preventDefault(); goTo(index + 1); }
        });

        // Pause while the visitor is looking/interacting, off-screen, or in another tab.
        var hovering = false, touching = false, offscreen = false, touchTimer = null;
        function sync() {
            root.classList.toggle('is-paused', reduceMotion || hovering || touching || offscreen || document.hidden);
        }
        root.addEventListener('mouseenter', function () { hovering = true; sync(); });
        root.addEventListener('mouseleave', function () { hovering = false; sync(); });
        root.addEventListener('focusin', function () { hovering = true; sync(); });
        root.addEventListener('focusout', function () { hovering = false; sync(); });
        track.addEventListener('touchstart', function () { touching = true; clearTimeout(touchTimer); sync(); }, { passive: true });
        track.addEventListener('touchend', function () {
            clearTimeout(touchTimer);
            touchTimer = setTimeout(function () { touching = false; sync(); }, 4000);
        });
        document.addEventListener('visibilitychange', sync);
        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (entries) { offscreen = !entries[0].isIntersecting; sync(); }).observe(root);
        }
    }

    /* ---------- Photo strip: endless marquee of the admin's "Show in hero" photos ----------
       The original set is repeated until it is wider than the screen, then the whole run is
       duplicated once; the CSS animation moves the track by exactly half, so the loop is
       seamless however many photos there are. Copies are hidden from screen readers and
       clicking one opens the lightbox on its original. */
    function initMarquee() {
        document.querySelectorAll('[data-marquee]').forEach(function (strip) {
            var track = strip.querySelector('.photo-strip__track');
            var originals = Array.prototype.slice.call(track.children);
            if (reduceMotion || !originals.length) return;

            var SPEED = 45; // pixels per second
            var builtFor = 0;

            function cloneOf(node) {
                var copy = node.cloneNode(true);
                var source = node.dataset.cloneOf !== undefined ? originals[+node.dataset.cloneOf] : node;
                copy.dataset.cloneOf = String(originals.indexOf(source));
                copy.removeAttribute('data-lightbox');
                copy.setAttribute('aria-hidden', 'true');
                copy.setAttribute('tabindex', '-1');
                return copy;
            }

            function build() {
                var available = strip.clientWidth;
                if (!available || Math.abs(available - builtFor) < 80) return;
                strip.classList.remove('is-ready');
                originals.forEach(function (o) { track.appendChild(o); });
                Array.prototype.slice.call(track.querySelectorAll('[data-clone-of]')).forEach(function (c) { c.remove(); });

                var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
                var setWidth = originals.reduce(function (w, o) { return w + o.getBoundingClientRect().width + gap; }, 0);
                if (!setWidth) return;
                var half = setWidth;
                while (half < available + 120) {
                    originals.forEach(function (o) { track.appendChild(cloneOf(o)); });
                    half += setWidth;
                }
                Array.prototype.slice.call(track.children).forEach(function (n) { track.appendChild(cloneOf(n)); });

                track.style.setProperty('--marquee-duration', (half / SPEED).toFixed(1) + 's');
                strip.style.setProperty('--marquee-duration', (half / SPEED).toFixed(1) + 's');
                builtFor = available;
                strip.classList.add('is-ready');
            }

            // Clicking a copy opens the lightbox on the original photo.
            track.addEventListener('click', function (e) {
                var copy = e.target.closest('[data-clone-of]');
                if (!copy) return;
                e.preventDefault();
                originals[+copy.dataset.cloneOf].click();
            });

            // Pause while off-screen, in a background tab, or being touched.
            var offscreen = false, touching = false, touchTimer = null;
            function sync() { strip.classList.toggle('is-paused', offscreen || touching || document.hidden); }
            if ('IntersectionObserver' in window) {
                new IntersectionObserver(function (entries) {
                    offscreen = !entries[0].isIntersecting;
                    if (!offscreen) build();
                    sync();
                }).observe(strip);
            }
            strip.addEventListener('touchstart', function () { touching = true; clearTimeout(touchTimer); sync(); }, { passive: true });
            strip.addEventListener('touchend', function () {
                clearTimeout(touchTimer);
                touchTimer = setTimeout(function () { touching = false; sync(); }, 2500);
            });
            document.addEventListener('visibilitychange', sync);
            var resizeTimer = null;
            window.addEventListener('resize', function () {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(build, 200);
            });

            // Measure only once the photos have their real widths.
            var imgs = originals.map(function (o) { return o.querySelector('img'); }).filter(Boolean);
            Promise.all(imgs.map(function (img) {
                if (img.complete && img.naturalWidth) return Promise.resolve();
                img.loading = 'eager';
                return new Promise(function (resolve) {
                    img.addEventListener('load', resolve, { once: true });
                    img.addEventListener('error', resolve, { once: true });
                });
            })).then(build);
        });
    }

    /* ---------- Lightbox (native <dialog>) ---------- */
    function initLightbox() {
        var links = document.querySelectorAll('[data-lightbox]');
        if (!links.length || typeof HTMLDialogElement !== 'function') return;

        var sprite = document.documentElement.dataset.icons || '';
        function icon(name) {
            return '<svg class="icon" aria-hidden="true"><use href="' + sprite + '#i-' + name + '"></use></svg>';
        }

        var dialog = document.createElement('dialog');
        dialog.className = 'lightbox';
        dialog.setAttribute('aria-label', 'Image viewer');
        dialog.innerHTML =
            '<button type="button" class="lightbox__btn lightbox__close" aria-label="Close">' + icon('x') + '</button>' +
            '<button type="button" class="lightbox__btn lightbox__prev" aria-label="Previous image">' + icon('chevron-left') + '</button>' +
            '<figure class="lightbox__figure"><img alt=""><figcaption></figcaption></figure>' +
            '<button type="button" class="lightbox__btn lightbox__next" aria-label="Next image">' + icon('chevron-right') + '</button>' +
            '<p class="lightbox__count" aria-live="polite"></p>';
        document.body.appendChild(dialog);

        var img = dialog.querySelector('img');
        var caption = dialog.querySelector('figcaption');
        var count = dialog.querySelector('.lightbox__count');
        var group = [];
        var pos = 0;

        function show(i) {
            pos = (i + group.length) % group.length;
            var link = group[pos];
            img.src = link.getAttribute('href');
            img.alt = link.dataset.caption || '';
            caption.textContent = link.dataset.caption || '';
            count.textContent = group.length > 1 ? (pos + 1) + ' / ' + group.length : '';
            dialog.classList.toggle('is-single', group.length < 2);
        }

        links.forEach(function (link) {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                var container = link.closest('[data-lightbox-group]');
                group = Array.prototype.slice.call(
                    (container || document).querySelectorAll('[data-lightbox]')
                );
                show(group.indexOf(link));
                dialog.showModal();
            });
        });

        dialog.querySelector('.lightbox__close').addEventListener('click', function () { dialog.close(); });
        dialog.querySelector('.lightbox__prev').addEventListener('click', function () { show(pos - 1); });
        dialog.querySelector('.lightbox__next').addEventListener('click', function () { show(pos + 1); });
        dialog.addEventListener('click', function (e) { if (e.target === dialog) dialog.close(); });
        dialog.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowLeft') show(pos - 1);
            if (e.key === 'ArrowRight') show(pos + 1);
        });
        dialog.addEventListener('close', function () { img.removeAttribute('src'); });

        var startX = null;
        dialog.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
        dialog.addEventListener('touchend', function (e) {
            if (startX === null) return;
            var dx = e.changedTouches[0].clientX - startX;
            if (Math.abs(dx) > 50) show(pos + (dx < 0 ? 1 : -1));
            startX = null;
        });
    }

    /* ---------- Click-to-load YouTube (no player JS until requested) ---------- */
    function initVideos() {
        document.querySelectorAll('.video-embed[data-youtube-id]').forEach(function (box) {
            var btn = box.querySelector('.video-embed__play');
            if (!btn) return;
            btn.addEventListener('click', function () {
                var id = encodeURIComponent(box.dataset.youtubeId);
                var iframe = document.createElement('iframe');
                iframe.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
                iframe.title = btn.getAttribute('aria-label').replace('Play video: ', '');
                iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
                iframe.allowFullscreen = true;
                box.innerHTML = '';
                box.appendChild(iframe);
                box.classList.add('is-playing');
            });
        });
    }

    /* ---------- Inline form validation ---------- */
    function initForms() {
        document.querySelectorAll('form[data-validate]').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                var firstInvalid = null;
                form.querySelectorAll('input, select, textarea').forEach(function (field) {
                    var wrap = field.closest('.field');
                    if (!wrap) return;
                    var valid = field.checkValidity();
                    wrap.classList.toggle('has-error', !valid);
                    var msg = wrap.querySelector('.field__error[data-client]');
                    if (!valid) {
                        if (!msg) {
                            msg = document.createElement('p');
                            msg.className = 'field__error';
                            msg.dataset.client = '1';
                            wrap.appendChild(msg);
                        }
                        msg.textContent = field.validationMessage;
                        firstInvalid = firstInvalid || field;
                    } else if (msg) {
                        msg.remove();
                    }
                });
                if (firstInvalid) {
                    e.preventDefault();
                    firstInvalid.focus();
                    return;
                }
                var submit = form.querySelector('[type="submit"]');
                if (submit) {
                    submit.disabled = true;
                    submit.classList.add('is-loading');
                }
            });
            form.addEventListener('input', function (e) {
                var wrap = e.target.closest('.field');
                if (wrap && e.target.checkValidity()) {
                    wrap.classList.remove('has-error');
                    var msg = wrap.querySelector('.field__error[data-client]');
                    if (msg) msg.remove();
                }
            });
        });
    }

    /* ---------- Flash messages ---------- */
    function initToasts() {
        document.querySelectorAll('.toast').forEach(function (toast, i) {
            var close = toast.querySelector('[data-dismiss-toast]');
            function hide() {
                toast.classList.add('is-leaving');
                setTimeout(function () { toast.remove(); }, 300);
            }
            if (close) close.addEventListener('click', hide);
            setTimeout(hide, 7000 + i * 800);
        });
    }

    /* ---------- Scroll reveal ----------
       Modern browsers: pure CSS scroll-driven animations (see style.css), nothing to do here.
       Others: an IntersectionObserver toggles .is-visible every time an element enters or
       leaves the screen, so reveals replay in both scroll directions. Elements are only
       hidden once they are off-screen, so nothing visible ever flickers. */
    var REVEAL = [
        '.section-head', '.why-content > .section-lead', '.card-grid > *', '.feature-grid > *', '.steps > *',
        '.bento__item', '.gallery-tile', '.team-card', '.value-card', '.highlight-strip li', '.thumb-grid > a',
        '.cta-band__inner', '.form-card', '.contact-panel', '.price-card', '.faq details', '.feature-post',
        '.fact-row', '.detail-list', '.empty-state', '.center-actions'
    ].join(',');
    var REVEAL_ZOOM = '.why-media, .split__media, .director__photo, .photo-grid';

    function initReveal() {
        if (reduceMotion || !('IntersectionObserver' in window)) return;
        if (window.CSS && CSS.supports && CSS.supports('animation-timeline: view()')) return;

        var observer = new IntersectionObserver(function (entries) {
            var shown = 0;
            entries.forEach(function (entry) {
                var el = entry.target;
                if (entry.isIntersecting) {
                    if (!el.hasAttribute('data-reveal')) return; // was on screen from the start
                    el.style.setProperty('--reveal-delay', Math.min(shown++ * 70, 350) + 'ms');
                    el.classList.add('is-visible');
                } else {
                    // Off-screen: reset, remembering which edge it left by so it re-enters from there.
                    el.setAttribute('data-reveal', el.dataset.revealKind);
                    el.setAttribute('data-reveal-from', entry.boundingClientRect.top < 0 ? 'top' : 'bottom');
                    el.style.removeProperty('--reveal-delay');
                    el.classList.remove('is-visible');
                }
            });
        }, { rootMargin: '0px 0px -6% 0px', threshold: 0 });

        function inSwipeRow(el) {
            var parent = el.parentElement;
            return parent && parent.classList.contains('card-grid--scroll') &&
                getComputedStyle(parent).overflowX !== 'visible';
        }

        function prepare(selector, kind) {
            document.querySelectorAll(selector).forEach(function (el) {
                // Cards in a sideways-swipe row (phones) reveal together with their row.
                if (inSwipeRow(el)) el = el.parentElement;
                if (el.dataset.revealKind || (el.parentElement && el.parentElement.closest('[data-reveal-kind]'))) return;
                el.dataset.revealKind = kind;
                observer.observe(el);
            });
        }
        prepare(REVEAL_ZOOM, 'zoom');
        prepare(REVEAL, 'up');
    }

    /* ---------- Hero parallax + header that tucks away while scrolling down ---------- */
    function initScrollEffects() {
        var header = document.getElementById('siteHeader');
        var hero = document.querySelector('.hero');
        var heroMedia = hero && hero.querySelector('.hero__ambient');
        var lastY = window.scrollY;
        var ticking = false;

        function update() {
            ticking = false;
            var y = window.scrollY;

            if (header) {
                var goingDown = y > lastY + 4;
                var goingUp = y < lastY - 4;
                if (goingDown && y > 320 && !document.body.classList.contains('nav-open')) header.classList.add('is-tucked');
                else if (goingUp || y < 120) header.classList.remove('is-tucked');
            }

            // Only the blurred ambient layer drifts; the headline and flyer showcase stay crisp.
            if (heroMedia && !reduceMotion && y < hero.offsetHeight) {
                heroMedia.style.transform = 'translate3d(0,' + (y * 0.35).toFixed(1) + 'px,0)';
            }
            lastY = y;
        }
        window.addEventListener('scroll', function () {
            if (!ticking) { ticking = true; requestAnimationFrame(update); }
        }, { passive: true });
    }

    /* ---------- Mobile action bar: "Ask AI" opens the chat widget ---------- */
    function initMobileBar() {
        document.querySelectorAll('[data-open-chat]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var toggle = document.getElementById('ai-chat-toggle');
                if (toggle) toggle.click();
            });
        });
    }

    function init() {
        initNav();
        initMobileBar();
        initReveal();
        initScrollEffects();
        initHeader();
        initShowcase();
        initLightbox();
        initVideos();
        initMarquee();
        initForms();
        initToasts();
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
}());
