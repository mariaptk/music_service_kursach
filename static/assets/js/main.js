// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Активация фильтров
    document.querySelectorAll('.filter-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // Добавление в избранное
    document.querySelectorAll('.action-btn .fa-heart').forEach(heart => {
        heart.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('fa-solid');
            this.classList.toggle('fa-regular');
            if (this.classList.contains('fa-solid')) {
                this.style.color = '#1DB954';
                this.parentElement.classList.add('active');
            } else {
                this.style.color = '';
                this.parentElement.classList.remove('active');
            }
        });
    });

    // Enter для поиска
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.closest('form').submit();
            }
        });
    }
});