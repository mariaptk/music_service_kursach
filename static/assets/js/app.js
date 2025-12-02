// Поиск треков
function searchTracks(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(tracks => {
            displaySearchResults(tracks);
        })
        .catch(error => {
            console.error('Ошибка поиска:', error);
        });
}

// Отображение результатов поиска
function displaySearchResults(tracks) {
    const resultsContainer = document.getElementById('searchResults');

    if (tracks.length === 0) {
        resultsContainer.innerHTML = '<p>Ничего не найдено</p>';
        return;
    }

    let html = '<div class="row">';

    tracks.forEach(track => {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${track.title}</h5>
                        <p class="card-text">Исполнитель: ${track.artist}</p>
                        <p class="card-text">Альбом: ${track.album}</p>
                        <button class="btn btn-primary btn-sm" onclick="playPreview('${track.preview}')">
                            Слушать
                        </button>
                        <button class="btn btn-success btn-sm" onclick="addToFavorites(${track.id})">
                            В избранное
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    resultsContainer.innerHTML = html;
}

// Воспроизведение превью
function playPreview(previewUrl) {
    if (previewUrl) {
        const audio = new Audio(previewUrl);
        audio.play();
    }
}

// Добавление в избранное
function addToFavorites(trackId) {
    // Получаем данные трека (упрощенно)
    const trackData = {
        id: trackId,
        title: 'Track Title',  // нужно будет доработать
        artist: 'Artist Name'
    };

    fetch('/api/favorites', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(trackData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Трек добавлен в избранное!');
        } else {
            alert('Ошибка добавления в избранное');
        }
    });
}

// Обработчик формы поиска
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('searchInput').value;
            if (query) {
                searchTracks(query);
            }
        });
    }
});