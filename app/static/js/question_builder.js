document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // Tab Navigation & Error Indicators
    // -------------------------------------------------------------
    const tabButtons = document.querySelectorAll('.form-tab-btn');
    const tabPanes = document.querySelectorAll('.form-tab-pane');

    function switchTab(tabName) {
        tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        tabPanes.forEach(pane => {
            pane.classList.toggle('active', pane.id === `tab-${tabName}`);
        });
    }

    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(btn.dataset.tab);
        });
    });

    // Check for validation errors on load and activate erroring tab
    tabPanes.forEach(pane => {
        if (pane.querySelector('.form-error')) {
            const tabName = pane.id.replace('tab-', '');
            switchTab(tabName);
            const badge = document.querySelector(`.form-tab-btn[data-tab="${tabName}"] .tab-badge`);
            if (badge) badge.classList.add('has-error');
        }
    });

    // -------------------------------------------------------------
    // Custom Category Handling
    // -------------------------------------------------------------
    const categorySelect = document.getElementById('category');
    const customCategoryGroup = document.getElementById('custom-category-group');
    const customCategoryInput = document.getElementById('custom_category');

    function updateCategoryVisibility() {
        if (!categorySelect || !customCategoryGroup) return;
        if (categorySelect.value === 'Other') {
            customCategoryGroup.style.display = 'block';
        } else {
            customCategoryGroup.style.display = 'none';
        }
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', () => {
            updateCategoryVisibility();
            const catVal = categorySelect.value === 'Other' ? (customCategoryInput ? customCategoryInput.value : '') : categorySelect.value;
            fetchSuggestions(catVal);
        });
        updateCategoryVisibility();
    }

    if (customCategoryInput) {
        customCategoryInput.addEventListener('blur', () => {
            if (categorySelect && categorySelect.value === 'Other') {
                fetchSuggestions(customCategoryInput.value);
            }
        });
    }

    // -------------------------------------------------------------
    // Question Builder State & UI
    // -------------------------------------------------------------
    const questionsContainer = document.getElementById('builder-questions-list');
    const questionsHiddenInput = document.getElementById('questions_json');
    const addQuestionBtn = document.getElementById('add-question-btn');
    const capWarning = document.getElementById('builder-cap-warning');
    const previewContainer = document.getElementById('builder-live-preview');
    const savedTemplateSelect = document.getElementById('saved-template-select');
    const applyTemplateBtn = document.getElementById('apply-template-btn');
    const saveTemplateBtn = document.getElementById('save-template-btn');

    let questions = [];

    // Parse existing questions if provided in page window data
    if (window.INITIAL_QUESTIONS && Array.isArray(window.INITIAL_QUESTIONS)) {
        questions = window.INITIAL_QUESTIONS.map((q, idx) => ({
            id: q.id || null,
            text: q.question_text || q.text || '',
            type: q.question_type || q.type || 'text',
            options: q.options ? (typeof q.options === 'string' ? JSON.parse(q.options) : q.options) : [],
            required: q.is_required !== undefined ? q.is_required : (q.required || false),
            display_order: idx
        }));
    }

    function syncHiddenInput() {
        if (!questionsHiddenInput) return;
        questions = questions.slice(0, 10);
        questionsHiddenInput.value = JSON.stringify(questions.map((q, idx) => ({
            id: q.id,
            text: q.text,
            type: q.type,
            options: q.options,
            required: q.required,
            display_order: idx
        })));
    }

    function renderBuilder() {
        if (!questionsContainer) return;
        questionsContainer.innerHTML = '';

        if (questions.length >= 10) {
            if (addQuestionBtn) addQuestionBtn.disabled = true;
            if (capWarning) capWarning.style.display = 'block';
        } else {
            if (addQuestionBtn) addQuestionBtn.disabled = false;
            if (capWarning) capWarning.style.display = 'none';
        }

        questions.forEach((q, index) => {
            const row = document.createElement('div');
            row.className = 'question-builder-row card mb-3 p-3';

            const isChoice = q.type === 'single_choice' || q.type === 'multi_choice';
            const optionsStr = Array.isArray(q.options) ? q.options.join(', ') : '';

            row.innerHTML = `
                <div class="d-flex align-items-center justify-content-between mb-2">
                    <div class="d-flex align-items-center gap-2">
                        <button type="button" class="btn btn-sm btn-outline-secondary move-up-btn" ${index === 0 ? 'disabled' : ''}>&uarr;</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary move-down-btn" ${index === questions.length - 1 ? 'disabled' : ''}>&darr;</button>
                        <span class="badge bg-secondary">Q${index + 1}</span>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger delete-q-btn">&times; Remove</button>
                </div>
                <div class="row g-2 mb-2">
                    <div class="col-md-7">
                        <input type="text" class="form-control q-text-input" placeholder="Question Wording" value="${escapeHtml(q.text)}">
                    </div>
                    <div class="col-md-3">
                        <select class="form-select q-type-select">
                            <option value="rating" ${q.type === 'rating' ? 'selected' : ''}>Rating (1-5 Stars)</option>
                            <option value="yes_no" ${q.type === 'yes_no' ? 'selected' : ''}>Yes / No</option>
                            <option value="single_choice" ${q.type === 'single_choice' ? 'selected' : ''}>Single Choice</option>
                            <option value="multi_choice" ${q.type === 'multi_choice' ? 'selected' : ''}>Multiple Choice</option>
                            <option value="text" ${q.type === 'text' ? 'selected' : ''}>Text Response</option>
                        </select>
                    </div>
                    <div class="col-md-2 d-flex align-items-center">
                        <div class="form-check form-switch mb-0">
                            <input class="form-check-input q-req-check" type="checkbox" id="req-${index}" ${q.required ? 'checked' : ''}>
                            <label class="form-check-label" for="req-${index}">Required</label>
                        </div>
                    </div>
                </div>
                <div class="options-container" style="display: ${isChoice ? 'block' : 'none'};">
                    <label class="form-label small text-muted">Options (comma separated):</label>
                    <input type="text" class="form-control form-control-sm q-options-input" placeholder="Option 1, Option 2, Option 3" value="${escapeHtml(optionsStr)}">
                </div>
            `;

            // Event Listeners for this row
            row.querySelector('.move-up-btn').addEventListener('click', () => moveQuestion(index, -1));
            row.querySelector('.move-down-btn').addEventListener('click', () => moveQuestion(index, 1));
            row.querySelector('.delete-q-btn').addEventListener('click', () => removeQuestion(index));

            const textInput = row.querySelector('.q-text-input');
            textInput.addEventListener('input', (e) => {
                questions[index].text = e.target.value;
                syncHiddenInput();
                renderPreview();
            });

            const typeSelect = row.querySelector('.q-type-select');
            typeSelect.addEventListener('change', (e) => {
                questions[index].type = e.target.value;
                const optsDiv = row.querySelector('.options-container');
                optsDiv.style.display = (e.target.value === 'single_choice' || e.target.value === 'multi_choice') ? 'block' : 'none';
                syncHiddenInput();
                renderPreview();
            });

            const reqCheck = row.querySelector('.q-req-check');
            reqCheck.addEventListener('change', (e) => {
                questions[index].required = e.target.checked;
                syncHiddenInput();
                renderPreview();
            });

            const optsInput = row.querySelector('.q-options-input');
            optsInput.addEventListener('input', (e) => {
                questions[index].options = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
                syncHiddenInput();
                renderPreview();
            });

            questionsContainer.appendChild(row);
        });

        syncHiddenInput();
        renderPreview();
    }

    function moveQuestion(index, direction) {
        const newIndex = index + direction;
        if (newIndex < 0 || newIndex >= questions.length) return;
        const temp = questions[index];
        questions[index] = questions[newIndex];
        questions[newIndex] = temp;
        renderBuilder();
    }

    function removeQuestion(index) {
        questions.splice(index, 1);
        renderBuilder();
    }

    if (addQuestionBtn) {
        addQuestionBtn.addEventListener('click', () => {
            if (questions.length >= 10) return;
            questions.push({
                id: null,
                text: '',
                type: 'rating',
                options: [],
                required: false,
                display_order: questions.length
            });
            renderBuilder();
        });
    }

    function escapeHtml(str) {
        return (str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // -------------------------------------------------------------
    // Live Preview Renderer
    // -------------------------------------------------------------
    function renderPreview() {
        if (!previewContainer) return;
        if (questions.length === 0) {
            previewContainer.innerHTML = '<div class="text-muted p-4 text-center">No questions added yet. Questions will appear here in real-time.</div>';
            return;
        }

        let html = '<div class="preview-mock-form p-3 border rounded bg-light">';
        html += '<h5 class="mb-3 text-primary"><i class="bi bi-eye"></i> Form Live Preview</h5>';

        questions.forEach((q, idx) => {
            html += `<div class="mb-3 p-2 bg-white rounded shadow-sm">
                <label class="form-label fw-bold small">${idx + 1}. ${escapeHtml(q.text) || 'Untitled Question'}${q.required ? ' <span class="text-danger">*</span>' : ''}</label>`;

            if (q.type === 'rating') {
                html += '<div class="star-rating-mock text-warning fs-5">★ ★ ★ ★ ★</div>';
            } else if (q.type === 'yes_no') {
                html += '<div><span class="btn btn-sm btn-outline-primary me-2">Yes</span><span class="btn btn-sm btn-outline-secondary">No</span></div>';
            } else if (q.type === 'single_choice') {
                const opts = q.options.length ? q.options : ['Option 1', 'Option 2'];
                opts.forEach(opt => {
                    html += `<div class="form-check"><input class="form-check-input" type="radio" disabled><label class="form-check-label small">${escapeHtml(opt)}</label></div>`;
                });
            } else if (q.type === 'multi_choice') {
                const opts = q.options.length ? q.options : ['Option 1', 'Option 2'];
                opts.forEach(opt => {
                    html += `<div class="form-check"><input class="form-check-input" type="checkbox" disabled><label class="form-check-label small">${escapeHtml(opt)}</label></div>`;
                });
            } else if (q.type === 'text') {
                html += '<textarea class="form-control form-control-sm" rows="2" placeholder="Attendee text response..." disabled></textarea>';
            }

            html += '</div>';
        });

        html += '</div>';
        previewContainer.innerHTML = html;
    }

    // -------------------------------------------------------------
    // Fetch Suggested Questions API
    // -------------------------------------------------------------
    async function fetchSuggestions(categoryText) {
        if (!categoryText) return;
        try {
            const resp = await fetch(`/api/suggested-questions?category=${encodeURIComponent(categoryText)}`);
            const data = await resp.json();

            if (data.suggested && data.suggested.length) {
                // If current questions are empty or user confirms replacement
                if (questions.length === 0 || window.confirm(`Load suggested questions for category "${categoryText}"?`)) {
                    questions = data.suggested.map((q, idx) => ({
                        id: null,
                        text: q.text,
                        type: q.type,
                        options: q.options || [],
                        required: q.required || false,
                        display_order: idx
                    }));
                    renderBuilder();
                }
            }
        } catch (err) {
            console.error('Error fetching suggested questions:', err);
        }
    }

    // -------------------------------------------------------------
    // Saved Templates Management
    // -------------------------------------------------------------
    async function loadSavedTemplates() {
        if (!savedTemplateSelect) return;
        try {
            const resp = await fetch('/api/saved-question-sets');
            if (!resp.ok) return;
            const templates = await resp.json();
            savedTemplateSelect.innerHTML = '<option value="">-- Select Saved Template --</option>';
            templates.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = t.name;
                opt.dataset.questions = JSON.stringify(t.questions);
                savedTemplateSelect.appendChild(opt);
            });
        } catch (err) {
            console.error('Error loading saved templates:', err);
        }
    }

    if (applyTemplateBtn && savedTemplateSelect) {
        applyTemplateBtn.addEventListener('click', () => {
            const selOpt = savedTemplateSelect.options[savedTemplateSelect.selectedIndex];
            if (!selOpt || !selOpt.dataset.questions) return;
            try {
                const tQuestions = JSON.parse(selOpt.dataset.questions);
                questions = tQuestions.map((q, idx) => ({
                    id: null,
                    text: q.text,
                    type: q.type,
                    options: q.options || [],
                    required: q.required || false,
                    display_order: idx
                }));
                renderBuilder();
            } catch (e) {
                console.error('Error applying template:', e);
            }
        });
    }

    if (saveTemplateBtn) {
        saveTemplateBtn.addEventListener('click', async () => {
            if (questions.length === 0) {
                alert('Add at least one question before saving a template.');
                return;
            }
            const name = prompt('Enter a name for this feedback template:');
            if (!name || !name.trim()) return;

            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            try {
                const resp = await fetch('/api/saved-question-sets', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        name: name.trim(),
                        questions: questions
                    })
                });
                const resData = await resp.json();
                if (resData.success) {
                    alert('Template saved successfully!');
                    loadSavedTemplates();
                } else {
                    alert(resData.error || 'Failed to save template.');
                }
            } catch (err) {
                console.error('Error saving template:', err);
            }
        });
    }

    // Initial load calls
    loadSavedTemplates();
    renderBuilder();
});
