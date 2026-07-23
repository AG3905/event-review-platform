document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reviewForm');
    if (!form) return;

    let currentStep = 1;
    const totalSteps = 4;

    const progressFill = document.getElementById('wizardProgressBar');
    const stepText = document.getElementById('step-indicator-text');
    const percentText = document.getElementById('step-percentage-text');
    const summaryContainer = document.getElementById('wizard-summary-container');

    const stepTitles = {
        1: 'Step 1 of 4: Rating & Recommendation',
        2: 'Step 2 of 4: Detailed Feedback Questions',
        3: 'Step 3 of 4: Attendee Information',
        4: 'Step 4 of 4: Summary & Final Submission'
    };

    // -------------------------------------------------------------
    // Star Rating Widget (Step 1)
    // -------------------------------------------------------------
    const stars = form.querySelectorAll('#starRating .star');
    const ratingInput = document.getElementById('star_rating');
    const ratingText = document.getElementById('ratingText');
    const ratingMessages = {
        1: '1/5 - Poor', 2: '2/5 - Fair',
        3: '3/5 - Good', 4: '4/5 - Very Good',
        5: '5/5 - Outstanding!'
    };

    const highlightStars = (rating) => {
        stars.forEach((star, idx) => {
            star.classList.toggle('text-warning', idx < rating);
            star.classList.toggle('text-muted', idx >= rating);
        });
    };

    stars.forEach(star => {
        star.addEventListener('click', () => {
            const r = parseInt(star.dataset.rating, 10);
            if (ratingInput) ratingInput.value = r;
            highlightStars(r);
            if (ratingText) ratingText.textContent = ratingMessages[r];
        });
    });

    // Dynamic question stars
    document.querySelectorAll('.q-star-rating').forEach(widget => {
        const qId = widget.dataset.qId;
        const qHidden = document.getElementById(`q_val_${qId}`);
        const qStars = widget.querySelectorAll('.q-star');

        qStars.forEach(st => {
            st.addEventListener('click', () => {
                const val = parseInt(st.dataset.val, 10);
                if (qHidden) qHidden.value = val;
                qStars.forEach((s, idx) => {
                    s.classList.toggle('text-warning', idx < val);
                    s.classList.toggle('text-muted', idx >= val);
                });
            });
        });
    });

    // -------------------------------------------------------------
    // Wizard Navigation & Step Display
    // -------------------------------------------------------------
    function updateProgress() {
        const pct = Math.round((currentStep / totalSteps) * 100);
        if (progressFill) progressFill.style.width = `${pct}%`;
        if (stepText) stepText.textContent = stepTitles[currentStep] || `Step ${currentStep} of ${totalSteps}`;
        if (percentText) percentText.textContent = `${pct}%`;
    }

    function showStep(stepNum) {
        document.querySelectorAll('.wizard-step').forEach(el => {
            const isTarget = parseInt(el.dataset.step, 10) === stepNum;
            el.style.display = isTarget ? 'block' : 'none';
            el.classList.toggle('active-step', isTarget);
        });

        currentStep = stepNum;
        updateProgress();

        if (currentStep === 4) {
            buildSummary();
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function validateCurrentStep() {
        if (currentStep === 1) {
            if (!ratingInput || !ratingInput.value) {
                alert('Please select an overall star rating before proceeding.');
                return false;
            }
        } else if (currentStep === 2) {
            // Check required dynamic questions
            const step2El = form.querySelector('.wizard-step[data-step="2"]');
            if (step2El) {
                const reqInputs = step2El.querySelectorAll('.required-q');
                for (let inp of reqInputs) {
                    const qText = inp.dataset.qText || 'a required question';
                    if (inp.type === 'radio') {
                        const name = inp.name;
                        const checked = step2El.querySelector(`input[name="${name}"]:checked`);
                        if (!checked) {
                            alert(`Please answer required question: "${qText}"`);
                            return false;
                        }
                    } else if (inp.type === 'checkbox') {
                        const name = inp.name;
                        const checked = step2El.querySelectorAll(`input[name="${name}"]:checked`);
                        if (!checked || checked.length === 0) {
                            alert(`Please select at least one option for: "${qText}"`);
                            return false;
                        }
                    } else if (!inp.value.trim()) {
                        alert(`Please answer required question: "${qText}"`);
                        inp.focus();
                        return false;
                    }
                }
            }
        } else if (currentStep === 3) {
            const nameEl = document.getElementById('reviewer_name');
            const emailEl = document.getElementById('reviewerEmail');

            if (!nameEl || !nameEl.value.trim()) {
                alert('Please enter your name.');
                if (nameEl) nameEl.focus();
                return false;
            }

            if (!emailEl || !emailEl.value.trim() || !emailEl.validity.valid) {
                alert('Please enter a valid email address.');
                if (emailEl) emailEl.focus();
                return false;
            }
        }

        return true;
    }

    form.querySelectorAll('.next-step-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (validateCurrentStep()) {
                showStep(currentStep + 1);
            }
        });
    });

    form.querySelectorAll('.prev-step-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentStep > 1) {
                showStep(currentStep - 1);
            }
        });
    });

    // -------------------------------------------------------------
    // Step 4 Summary Generator
    // -------------------------------------------------------------
    function buildSummary() {
        if (!summaryContainer) return;

        const nameVal = document.getElementById('reviewer_name')?.value || '';
        const emailVal = document.getElementById('reviewerEmail')?.value || '';
        const ratingVal = ratingInput?.value || 'Not selected';
        const reviewTextVal = document.getElementById('review_text')?.value || '';
        const townVal = document.getElementById('reviewer_town')?.value || '';
        const stateVal = document.getElementById('reviewer_state')?.value || '';

        let html = `
            <div class="card p-3 mb-3 bg-light border">
                <div class="d-flex justify-content-between align-items-center mb-2 border-bottom pb-2">
                    <span class="fw-bold text-dark"><i class="fas fa-star text-warning"></i> Rating & Recommendation</span>
                    <button type="button" class="btn btn-sm btn-link text-decoration-none jump-step-btn" data-jump="1">Edit</button>
                </div>
                <div class="small">
                    <div><strong>Rating:</strong> ${ratingVal} / 5 Stars</div>
                </div>
            </div>

            <div class="card p-3 mb-3 bg-light border">
                <div class="d-flex justify-content-between align-items-center mb-2 border-bottom pb-2">
                    <span class="fw-bold text-dark"><i class="fas fa-list-check text-primary"></i> Detailed Answers</span>
                    <button type="button" class="btn btn-sm btn-link text-decoration-none jump-step-btn" data-jump="2">Edit</button>
                </div>
                <div class="small">
        `;

        // Gather dynamic question answers
        const step2 = form.querySelector('.wizard-step[data-step="2"]');
        if (step2) {
            const items = step2.querySelectorAll('.dynamic-question-item');
            if (items.length > 0) {
                items.forEach((item, idx) => {
                    const label = item.querySelector('label')?.textContent.trim() || `Question ${idx + 1}`;
                    let ansText = 'No answer';

                    const textInp = item.querySelector('textarea, input[type="text"]');
                    const hiddenRating = item.querySelector('input[type="hidden"]');
                    const checkedRadio = item.querySelector('input[type="radio"]:checked');
                    const checkedBoxes = Array.from(item.querySelectorAll('input[type="checkbox"]:checked')).map(c => c.value);

                    if (hiddenRating && hiddenRating.value) {
                        ansText = `${hiddenRating.value} Stars`;
                    } else if (checkedRadio) {
                        ansText = checkedRadio.value;
                    } else if (checkedBoxes.length > 0) {
                        ansText = checkedBoxes.join(', ');
                    } else if (textInp && textInp.value.trim()) {
                        ansText = textInp.value.trim();
                    }

                    html += `<div class="mb-1"><strong>${label}:</strong> <span class="text-secondary">${escapeHtml(ansText)}</span></div>`;
                });
            } else {
                html += '<div class="text-muted">No dynamic questions configured.</div>';
            }

            if (reviewTextVal) {
                html += `<div class="mt-2 pt-2 border-top"><strong>Written Comments:</strong> <p class="mb-0 text-secondary">${escapeHtml(reviewTextVal)}</p></div>`;
            }
        }

        html += `
                </div>
            </div>

            <div class="card p-3 mb-3 bg-light border">
                <div class="d-flex justify-content-between align-items-center mb-2 border-bottom pb-2">
                    <span class="fw-bold text-dark"><i class="fas fa-user text-info"></i> Attendee Info</span>
                    <button type="button" class="btn btn-sm btn-link text-decoration-none jump-step-btn" data-jump="3">Edit</button>
                </div>
                <div class="small">
                    <div><strong>Name:</strong> ${escapeHtml(nameVal)}</div>
                    <div><strong>Email:</strong> ${escapeHtml(emailVal)}</div>
        `;

        if (townVal || stateVal) {
            html += `<div><strong>Location:</strong> ${escapeHtml(townVal)}${townVal && stateVal ? ', ' : ''}${escapeHtml(stateVal)} <span class="badge bg-secondary">Private</span></div>`;
        }

        html += `
                </div>
            </div>
        `;

        summaryContainer.innerHTML = html;

        summaryContainer.querySelectorAll('.jump-step-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                showStep(parseInt(btn.dataset.jump, 10));
            });
        });
    }

    function escapeHtml(str) {
        return (str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // -------------------------------------------------------------
    // Email Check API Integration
    // -------------------------------------------------------------
    const emailInput = document.getElementById('reviewerEmail');
    const emailMsg = document.getElementById('emailCheckMessage');
    let emailTimeout;

    if (emailInput) {
        emailInput.addEventListener('input', () => {
            clearTimeout(emailTimeout);
            if (!emailInput.value || !emailInput.validity.valid) {
                if (emailMsg) emailMsg.textContent = '';
                return;
            }
            emailTimeout = setTimeout(async () => {
                try {
                    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
                    const resp = await fetch('/api/check-email', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            email: emailInput.value,
                            unique_code: form.dataset.eventCode
                        })
                    });
                    const data = await resp.json();
                    if (emailMsg) {
                        emailMsg.textContent = data.exists ? data.message : '';
                        emailMsg.className = data.exists ? 'email-check-message text-danger small mt-1 fw-bold' : 'email-check-message text-success small mt-1';
                    }
                } catch (e) {
                    console.error('Error checking email:', e);
                }
            }, 500);
        });
    }

    // Submit handler
    form.addEventListener('submit', () => {
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.value = 'Submitting Review...';
        }
    });

    showStep(1);
});
