document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('sortReviews');
    const container = document.getElementById('reviewsContainer');
    if (!select || !container) return;
    select.addEventListener('change', () => {
        const direction = { newest: ['date', -1], oldest: ['date', 1], highest: ['rating', -1], lowest: ['rating', 1] }[select.value];
        [...container.children].sort((a, b) => direction[1] * (Number(a.dataset[direction[0]]) - Number(b.dataset[direction[0]]))).forEach((item) => container.append(item));
    });
});
