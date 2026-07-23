// Live Updates Background Polling Utility
const POLL_INTERVAL_MS = 15000;

document.addEventListener('DOMContentLoaded', () => {
    let timerId = null;
    let lastReviewTimestamp = null;

    function startPolling() {
        if (timerId) clearInterval(timerId);
        timerId = setInterval(pollForUpdates, POLL_INTERVAL_MS);
    }

    function stopPolling() {
        if (timerId) {
            clearInterval(timerId);
            timerId = null;
        }
    }

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            stopPolling();
        } else {
            pollForUpdates();
            startPolling();
        }
    });

    async function pollForUpdates() {
        const path = window.location.pathname;

        // 1. Event Details Page
        const eventMatch = path.match(/\/event\/(\d+)$/);
        if (eventMatch) {
            const eventId = eventMatch[1];
            try {
                let url = `/api/event/${eventId}/review-count`;
                if (lastReviewTimestamp) {
                    url += `?since=${encodeURIComponent(lastReviewTimestamp)}`;
                }
                const resp = await fetch(url);
                if (!resp.ok) return;
                const data = await resp.json();

                if (data.last_review_at) {
                    lastReviewTimestamp = data.last_review_at;
                }

                // Update total reviews count stat number
                const statCards = document.querySelectorAll('.stat-card');
                if (statCards.length >= 2) {
                    const totalNumEl = statCards[0].querySelector('.stat-number');
                    if (totalNumEl && parseInt(totalNumEl.textContent, 10) !== data.total_reviews) {
                        totalNumEl.textContent = data.total_reviews;
                    }

                    const avgNumEl = statCards[1].querySelector('.stat-number');
                    if (avgNumEl && parseFloat(avgNumEl.textContent) !== data.average_rating) {
                        avgNumEl.textContent = Number(data.average_rating).toFixed(1);
                    }
                }

                // If new reviews arrived, prepend to reviews container
                if (data.new_reviews && data.new_reviews.length > 0) {
                    const container = document.querySelector('.reviews-container');
                    if (container) {
                        data.new_reviews.forEach(r => {
                            const card = document.createElement('div');
                            card.className = 'review-card new-polled-card';
                            card.setAttribute('data-review-id', r.id);
                            card.innerHTML = `
                                <div class="review-header">
                                    <div class="review-author">
                                        <strong>${escapeHtml(r.reviewer_name)}</strong>
                                        <span class="badge bg-success ms-2">New</span>
                                    </div>
                                    <div class="review-rating">
                                        ${'★'.repeat(r.star_rating)}${'☆'.repeat(5 - r.star_rating)}
                                    </div>
                                </div>
                                <div class="review-text">${escapeHtml(r.review_text || '')}</div>
                            `;
                            container.prepend(card);
                        });
                        if (window.showAlert) {
                            window.showAlert('success', `${data.new_reviews.length} new review(s) received!`);
                        }
                    }
                }
            } catch (err) {
                console.error('Polling error (event details):', err);
            }
            return;
        }

        // 2. Organizer Dashboard
        if (path === '/dashboard' || path === '/dashboard/') {
            try {
                const resp = await fetch('/api/dashboard/summary');
                if (!resp.ok) return;
                const data = await resp.json();

                updateStatCardNumber('total-events-stat', data.total_events);
                updateStatCardNumber('total-reviews-stat', data.total_reviews);
                updateStatCardNumber('avg-rating-stat', data.avg_rating);
            } catch (err) {
                console.error('Polling error (dashboard):', err);
            }
            return;
        }

        // 3. Admin Dashboard
        if (path === '/admin' || path === '/admin/') {
            try {
                const resp = await fetch('/api/admin/summary');
                if (!resp.ok) return;
                const data = await resp.json();

                updateStatCardNumber('admin-total-organizers', data.total_organizers);
                updateStatCardNumber('admin-total-events', data.total_events);
                updateStatCardNumber('admin-total-reviews', data.total_reviews);
                updateStatCardNumber('admin-avg-rating', data.avg_rating);
            } catch (err) {
                console.error('Polling error (admin summary):', err);
            }
            return;
        }
    }

    function updateStatCardNumber(elemId, newVal) {
        const el = document.getElementById(elemId);
        if (el) {
            el.textContent = newVal;
        }
    }

    function escapeHtml(str) {
        return (str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // Start background polling
    startPolling();
});
