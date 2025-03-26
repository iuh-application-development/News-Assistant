
## Các bước cài đặt

### 1. Clone repository 
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Tạo và kích hoạt môi trường ảo (Virtual Environment)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 4. Cấu hình cơ sở dữ liệu
- Mở file `settings.py` trong thư mục `config`
- Cập nhật các thông tin cấu hình cơ sở dữ liệu nếu cần thiết

### 5. Chạy migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo tài khoản superuser (quản trị viên)
```bash
python manage.py createsuperuser
```

### 7. Chạy server
```bash
python manage.py runserver
```

### 8. Truy cập website
- Mở trình duyệt web và truy cập: `http://127.0.0.1:8000`
