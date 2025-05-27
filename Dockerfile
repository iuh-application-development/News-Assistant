# Sử dụng image chính thức của Python
FROM python:3.10

# Cài đặt biến môi trường để không tạo .pyc file
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Cập nhật pip và cài đặt các thư viện phụ thuộc
RUN pip install --upgrade pip

# Tạo thư mục app trong container và đặt làm thư mục làm việc
WORKDIR /app

# Sao chép requirements.txt và cài đặt
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Sao chép toàn bộ source code
COPY . /app/

# Mở cổng 8000
EXPOSE 8000

# Chạy lệnh khởi động server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
