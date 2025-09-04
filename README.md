## MyCoin-Blockchain2025

MyCoin-Blockchain2025 là một ứng dụng ví tiền điện tử và blockchain đơn giản được xây dựng bằng Python, Django và Django Channels. Dự án mô phỏng các chức năng cốt lõi của một hệ thống blockchain: tạo ví, gửi giao dịch, cơ chế đồng thuận Proof of Work (PoW) và cập nhật giao diện theo thời gian thực qua WebSocket.

---

### Tính năng nổi bật

- **Quản lý ví:** Tạo ví blockchain mới với cặp khóa Public/Private an toàn (ECDSA).
- **Giao dịch:** Gửi và nhận MyCoin giữa các ví trong hệ thống.
- **Cập nhật real-time:** Tự động cập nhật số dư và lịch sử giao dịch trên trang chủ ngay khi nhận được tiền mà không cần F5 (WebSocket/Django Channels).
- **Proof of Work:** Mỗi giao dịch được "khai thác" (mine) để tìm Nonce hợp lệ, đảm bảo tính toàn vẹn và bảo mật cho chuỗi giao dịch.
- **Lịch sử & chi tiết:** Xem lại toàn bộ lịch sử giao dịch và chi tiết kỹ thuật (hash, nonce, previous hash).
- **Giao diện hiện đại:** Giao diện người dùng thân thiện với Bootstrap 5.

---

### Công nghệ sử dụng

- **Backend:** Python, Django
- **Real-time:** Django Channels (WebSocket), Daphne ASGI Server
- **Frontend:** HTML, Bootstrap 5, JavaScript
- **Cơ sở dữ liệu:** SQLite 3 (mặc định của Django)
- **Mã hóa:** Thư viện `ecdsa` cho việc tạo và quản lý khóa

---

## Hướng dẫn cài đặt

### 1. Chuẩn bị môi trường

- Đảm bảo đã cài đặt Python 3.10 trở lên.
- Clone repository về máy:

```bash
git clone https://your-repository-url/MyCoin-Blockchain2025.git
cd MyCoin-Blockchain2025
```

### 2. Thiết lập môi trường ảo (khuyến nghị)

- Tạo môi trường ảo:

```bash
python -m venv venv
```

- Kích hoạt môi trường ảo:
    - **Windows:**  
      ```bash
      .\venv\Scripts\activate
      ```
    - **macOS/Linux:**  
      ```bash
      source venv/bin/activate
      ```

### 3. Cài đặt các gói phụ thuộc

```bash
pip install -r requirements.txt
```

### 4. Thiết lập cơ sở dữ liệu

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Tạo tài khoản admin

```bash
python manage.py createsuperuser
```
- Làm theo hướng dẫn để nhập tên đăng nhập, mật khẩu và email (có thể bỏ trống).

### 6. Khởi chạy server

- Dự án sử dụng Django Channels, cần chạy với Daphne:

```bash
python -m daphne blockchain.asgi:application
```

> **Lưu ý:** Không dùng `python manage.py runserver` vì không hỗ trợ đầy đủ WebSocket cho môi trường production.

- Truy cập ứng dụng tại: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Hướng dẫn sử dụng

1. **Tạo ví mới:** Đăng nhập và tạo ví blockchain cá nhân.
2. **Gửi/nhận MyCoin:** Thực hiện giao dịch giữa các ví.
3. **Theo dõi real-time:** Số dư và lịch sử giao dịch sẽ tự động cập nhật khi có thay đổi.
4. **Xem chi tiết giao dịch:** Truy cập lịch sử để xem thông tin kỹ thuật từng giao dịch.

---

