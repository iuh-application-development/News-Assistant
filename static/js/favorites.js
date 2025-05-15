document.addEventListener('DOMContentLoaded', function() {
    console.log('Favorites.js loaded');
    
    initFavoriteButtons();

    // Xử lý xóa khỏi yêu thích
    const removeButtons = document.querySelectorAll('.remove-from-favorites');
    console.log('Found remove buttons:', removeButtons.length);
    
    removeButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Remove button clicked');
            
            const link = this.getAttribute('data-link');
            removeFromFavorites(link, this);
        });
    });
});

function initFavoriteButtons() {
    const addButtons = document.querySelectorAll('.add-to-favorites');
    console.log('Init add-to-favorites buttons:', addButtons.length);
    addButtons.forEach(function(button) {
        // Remove old event listener if any by cloning
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Add button clicked');
            const article = {
                title: this.getAttribute('data-title'),
                link: this.getAttribute('data-link'),
                image: this.getAttribute('data-image'),
                description: this.getAttribute('data-description'),
                source: this.getAttribute('data-source'),
                pub_date: this.getAttribute('data-pub_date')
            };
            console.log('Article data:', article);
            addToFavorites(article, this);
        });
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function addToFavorites(article, button) {
    const confirmed = confirm("Thêm bài viết này vào yêu thích?");
    if (!confirmed) return;

    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang thêm...';

    // Lấy CSRF token từ cookie
    const csrfToken = getCookie('csrftoken');
    console.log('CSRF Token:', csrfToken ? 'Found' : 'Not found');
    console.log('Article gửi lên:', article);

    fetch('/favorites/add/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(article)
    })
    .then(res => {
        console.log('Response status:', res.status);
        return res.json().then(data => ({status: res.status, data}));
    })
    .then(({status, data}) => {
        console.log('Response data:', data);
        if (status === 401) {
            window.location.href = '/login/?next=' + window.location.pathname;
            return;
        }
        if (data) {
            if (data.message) {
                button.classList.remove('btn-success');
                button.classList.add('btn-secondary');
                button.innerHTML = '<i class="fas fa-check"></i> Đã thêm vào yêu thích';
                button.disabled = true;
            } else {
                button.disabled = false;
                button.classList.remove('btn-secondary');
                button.classList.add('btn-success');
                button.innerHTML = '<i class="fas fa-heart"></i> Thêm vào yêu thích';
            }
            alert(data.message || data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.disabled = false;
        button.classList.remove('btn-secondary');
        button.classList.add('btn-success');
        button.innerHTML = '<i class="fas fa-heart"></i> Thêm vào yêu thích';
        alert('Có lỗi xảy ra khi thêm vào yêu thích');
    });
}

function removeFromFavorites(link, button) {
    const confirmed = confirm("Bạn có chắc muốn xóa bài viết này khỏi danh sách yêu thích?");
    if (!confirmed) return;

    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xóa...';

    // Lấy CSRF token từ cookie
    const csrfToken = getCookie('csrftoken');
    console.log('CSRF Token for remove:', csrfToken ? 'Found' : 'Not found');

    fetch('/favorites/remove/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            link: link
        })
    })
    .then(res => {
        console.log('Remove response status:', res.status);
        if (res.status === 401) {
            window.location.href = '/login/?next=' + window.location.pathname;
            return;
        }
        return res.json();
    })
    .then(data => {
        console.log('Remove response data:', data);
        if (data && data.status === 'success') {
            // Remove the card from the DOM
            const card = button.closest('.col-md-4');
            card.remove();
            
            // Check if there are any remaining favorites
            const remainingCards = document.querySelectorAll('.col-md-4');
            if (remainingCards.length === 0) {
                // Show the "no favorites" message
                const container = document.querySelector('.container');
                container.innerHTML = `
                    <h2 class="mb-4">Danh sách yêu thích của bạn</h2>
                    <div class="alert alert-info">
                        <p class="mb-0">Bạn chưa có mục yêu thích nào.</p>
                    </div>
                `;
            }
        } else {
            // Restore button state
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-trash"></i> Xóa khỏi yêu thích';
            alert(data.error || 'Có lỗi xảy ra khi xóa mục yêu thích');
        }
    })
    .catch(error => {
        console.error('Remove error:', error);
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-trash"></i> Xóa khỏi yêu thích';
        alert('Có lỗi xảy ra khi xóa mục yêu thích');
    });
} 