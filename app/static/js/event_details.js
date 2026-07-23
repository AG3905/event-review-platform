document.addEventListener('DOMContentLoaded', () => {
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrf = csrfMeta ? csrfMeta.content : '';

    // Tab buttons
    document.querySelectorAll('.tab-button').forEach((button) => button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button, .tab-pane').forEach((item) => item.classList.remove('active'));
        button.classList.add('active');
        const pane = document.getElementById(`${button.dataset.tab}-tab`);
        if (pane) pane.classList.add('active');
    }));

    // Copy buttons - NO RELOAD
    document.querySelectorAll('.copy-btn').forEach((button) => button.addEventListener('click', async () => {
        const target = document.getElementById(button.dataset.target);
        if (!target) return;
        const origText = button.innerHTML;
        await navigator.clipboard.writeText(target.value);
        button.classList.add('btn-success');
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
            button.classList.remove('btn-success');
            button.innerHTML = origText;
        }, 2000);
    }));

    // Feature and Delete action handlers
    document.querySelectorAll('.feature-btn, .delete-btn').forEach((button) => button.addEventListener('click', async () => {
        const deleting = button.classList.contains('delete-btn');
        if (deleting && !window.confirm('Are you sure you want to delete this review?')) return;

        try {
            const response = await fetch(`/api/review/${button.dataset.reviewId}/${deleting ? 'delete' : 'feature'}`, {
                method: deleting ? 'DELETE' : 'POST',
                headers: { 'X-CSRFToken': csrf }
            });
            const data = await response.json();
            if (!data.success) {
                if (window.showAlert) window.showAlert('error', data.error || 'Unable to update review.');
                return;
            }

            if (deleting) {
                const card = button.closest('.review-card');
                if (card) {
                    card.style.transition = 'opacity 0.3s ease';
                    card.style.opacity = '0';
                    setTimeout(() => card.remove(), 300);
                }
            } else {
                button.classList.toggle('featured', data.is_featured);
                button.innerHTML = `<i class="fas fa-star"></i> ${data.is_featured ? 'Unfeature' : 'Feature'}`;
            }
            if (window.showAlert) window.showAlert('success', data.message);
        } catch (err) {
            console.error('Action error:', err);
        }
    }));
});
