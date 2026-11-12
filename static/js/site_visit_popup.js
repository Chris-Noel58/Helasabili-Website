(function () {
    const popup = document.getElementById('site-visit-popup');
    if (!popup) {
        return;
    }

    const form = popup.querySelector('.site-visit-popup__form');
    const closeButton = popup.querySelector('.site-visit-popup__close');
    const feedback = popup.querySelector('.site-visit-popup__feedback');
    const submitButton = popup.querySelector('.site-visit-popup__submit');
    const storageKey = 'helasabiliSiteVisitPromptDismissed';

    function wasDismissed() {
        try {
            return window.sessionStorage.getItem(storageKey) === '1';
        } catch (error) {
            console.warn('Site visit prompt preference could not be read.', error);
            return false;
        }
    }

    function markDismissed() {
        try {
            window.sessionStorage.setItem(storageKey, '1');
        } catch (error) {
            console.warn('Site visit prompt preference could not be saved.', error);
        }
    }

    function dismiss() {
        popup.classList.remove('is-visible');
        popup.hidden = true;
        markDismissed();
    }

    if (!wasDismissed()) {
        window.setTimeout(function () {
            if (!popup.hidden) {
                return;
            }
            popup.hidden = false;
            window.requestAnimationFrame(function () {
                popup.classList.add('is-visible');
            });
        }, 4500);
    }

    closeButton.addEventListener('click', dismiss);

    form.addEventListener('input', function (event) {
        event.target.removeAttribute('aria-invalid');
    });

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        feedback.hidden = true;
        feedback.classList.remove('is-error');
        form.querySelectorAll('[aria-invalid="true"]').forEach(function (field) {
            field.removeAttribute('aria-invalid');
        });
        submitButton.disabled = true;
        submitButton.textContent = 'Sending request...';

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const result = await response.json();

            if (!response.ok) {
                const errorMessages = [];
                Object.keys(result.errors || {}).forEach(function (fieldName) {
                    const field = form.elements.namedItem(fieldName);
                    if (field) {
                        field.setAttribute('aria-invalid', 'true');
                    }
                    (result.errors[fieldName] || []).forEach(function (error) {
                        errorMessages.push(error.message);
                    });
                });
                feedback.textContent = errorMessages.join(' ') || 'Please review your details and try again.';
                feedback.classList.add('is-error');
                feedback.hidden = false;
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-calendar-check" aria-hidden="true"></i> Request a site visit';
                return;
            }

            feedback.textContent = result.message;
            feedback.hidden = false;
            form.hidden = true;
            markDismissed();
        } catch (error) {
            console.error('Site visit request could not be submitted.', error);
            feedback.textContent = 'We could not send your request. Please try again.';
            feedback.classList.add('is-error');
            feedback.hidden = false;
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-calendar-check" aria-hidden="true"></i> Request a site visit';
        }
    });
})();
