document.addEventListener('DOMContentLoaded', () => {
    const csrf = document.querySelector('meta[name="csrf-token"]').content;
    document.querySelectorAll('.tab-button').forEach((button) => button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button, .tab-pane').forEach((item) => item.classList.remove('active'));
        button.classList.add('active'); document.getElementById(`${button.dataset.tab}-tab`).classList.add('active');
    }));
    document.querySelectorAll('.copy-btn').forEach((button) => button.addEventListener('click', async () => {
        const target = document.getElementById(button.dataset.target); await navigator.clipboard.writeText(target.value); button.classList.add('btn-success'); button.textContent = 'Copied!'; setTimeout(() => window.location.reload(), 1200);
    }));
    document.querySelectorAll('.feature-btn, .delete-btn').forEach((button) => button.addEventListener('click', async () => {
        const deleting = button.classList.contains('delete-btn');
        if (deleting && !window.confirm('Are you sure you want to delete this review?')) return;
        const response = await fetch(`/api/review/${button.dataset.reviewId}/${deleting ? 'delete' : 'feature'}`, { method: deleting ? 'DELETE' : 'POST', headers: { 'X-CSRFToken': csrf } });
        const data = await response.json(); if (!data.success) return window.showAlert('error', data.error || 'Unable to update review.');
        if (deleting) button.closest('.review-card').remove(); else button.classList.toggle('featured', data.is_featured);
        window.showAlert('success', data.message);
    }));
});
