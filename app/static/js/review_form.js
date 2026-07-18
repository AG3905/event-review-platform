document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reviewForm');
    if (!form) return;

    let currentStep = 1;
    const totalSteps = 4;
    const stars = form.querySelectorAll('.star');
    const ratingInput = document.getElementById('star_rating');
    const ratingText = document.getElementById('ratingText');
    const progress = document.getElementById('progressFill');
    const messages = {
        1: 'Poor - Needs significant improvement', 2: 'Fair - Below expectations',
        3: 'Good - Met expectations', 4: 'Very Good - Exceeded expectations',
        5: 'Excellent - Outstanding experience!'
    };

    const highlight = (rating) => stars.forEach((star, index) => star.classList.toggle('active', index < rating));
    const updateProgress = () => {
        progress.value = currentStep;
        form.querySelectorAll('.progress-step').forEach((step, index) => step.classList.toggle('active', index < currentStep));
    };
    const showStep = (nextStep) => {
        form.querySelector(`[data-step="${currentStep}"]`).classList.remove('active');
        currentStep = nextStep;
        form.querySelector(`[data-step="${currentStep}"]`).classList.add('active');
        updateProgress();
    };
    const validStep = () => {
        if (currentStep === 1) {
            const name = document.getElementById('reviewer_name');
            const email = document.getElementById('reviewerEmail');
            if (!name.value.trim() || !email.value.trim() || !email.validity.valid) {
                window.showAlert('error', 'Please provide a valid name and email address.');
                return false;
            }
        }
        if (currentStep === 2 && !ratingInput.value) {
            window.showAlert('error', 'Please select a rating.');
            return false;
        }
        return true;
    };

    stars.forEach((star) => {
        star.addEventListener('mouseenter', () => { const rating = Number(star.dataset.rating); highlight(rating); ratingText.textContent = messages[rating]; });
        star.addEventListener('click', () => { const rating = Number(star.dataset.rating); ratingInput.value = rating; highlight(rating); ratingText.textContent = messages[rating]; });
    });
    form.querySelector('.star-rating').addEventListener('mouseleave', () => {
        const rating = Number(ratingInput.value || 0); highlight(rating); ratingText.textContent = rating ? messages[rating] : 'Click a star to rate';
    });
    form.querySelectorAll('.next-step').forEach((button) => button.addEventListener('click', () => { if (validStep() && currentStep < totalSteps) showStep(currentStep + 1); }));
    form.querySelectorAll('.prev-step').forEach((button) => button.addEventListener('click', () => { if (currentStep > 1) showStep(currentStep - 1); }));

    const email = document.getElementById('reviewerEmail');
    const message = document.getElementById('emailCheckMessage');
    let timeout;
    email.addEventListener('input', () => {
        clearTimeout(timeout);
        if (!email.value || !email.validity.valid) { message.textContent = ''; return; }
        timeout = setTimeout(async () => {
            try {
                const response = await fetch('/api/check-email', {
                    method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content },
                    body: JSON.stringify({ email: email.value, unique_code: form.dataset.eventCode })
                });
                const data = await response.json();
                message.textContent = data.exists ? data.message : '';
                message.classList.toggle('error', Boolean(data.exists));
            } catch (_) { message.textContent = ''; }
        }, 500);
    });
    const textarea = document.getElementById('review_text');
    const count = document.getElementById('charCount');
    textarea.addEventListener('input', () => { count.textContent = textarea.value.length; });
    form.addEventListener('submit', () => { const submit = document.getElementById('submitBtn'); submit.disabled = true; submit.value = 'Submitting...'; });
    updateProgress();
});
