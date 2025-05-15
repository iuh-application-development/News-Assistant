document.addEventListener('DOMContentLoaded', function() {
    // Các biến cần thiết
    const loadMoreBtn = document.getElementById('load-more-btn');
    const newsContainer = document.getElementById('news-container');
    let page = 1;
    
    // Kiểm tra xem nút Load More có tồn tại không
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            // Tăng số trang
            page++;
            
            // Hiển thị trạng thái đang tải
            loadMoreBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang tải...';
            loadMoreBtn.disabled = true;
            
            // URL hiện tại (có thể có các tham số khác như feed=...)
            const currentUrl = window.location.href;
            // Tạo URL cho request Ajax
            const ajaxUrl = `/load-more-news/?page=${page}` + 
                (currentUrl.includes('feed=') ? '&' + currentUrl.split('?')[1] : '');
            
            // Thực hiện Ajax request
            fetch(ajaxUrl)
                .then(response => response.json())
                .then(data => {
                    // Thêm các bài viết mới vào container
                    if (data.html) {
                        // Thêm HTML mới vào cuối container
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = data.html;
                        
                        // Thêm từng phần tử con vào container
                        while (tempDiv.firstChild) {
                            newsContainer.appendChild(tempDiv.firstChild);
                        }
                        
                        // Gọi lại hàm gắn sự kiện yêu thích nếu có
                        if (typeof initFavoriteButtons === 'function') {
                            initFavoriteButtons();
                        }
                        
                        // Khôi phục trạng thái nút
                        loadMoreBtn.innerHTML = 'Xem thêm';
                        loadMoreBtn.disabled = false;
                        
                        // Ẩn nút nếu không còn bài viết
                        if (data.has_more === false) {
                            loadMoreBtn.style.display = 'none';
                        }
                    } else {
                        // Ẩn nút nếu không có dữ liệu trả về
                        loadMoreBtn.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Lỗi khi tải thêm tin:', error);
                    loadMoreBtn.innerHTML = 'Thử lại';
                    loadMoreBtn.disabled = false;
                });
        });
    }
});