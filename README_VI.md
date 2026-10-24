# Systemd Service Manager

Plugin aaPanel giúp quản lý các systemd service trên máy chủ Linux từ giao diện aaPanel.

[English](README.md)

## Tính năng

- Xem danh sách service, trạng thái chạy/dừng/lỗi và trạng thái tự khởi động cùng hệ thống.
- Tìm kiếm, lọc service theo trạng thái; xem riêng service tùy chỉnh.
- Khởi động, dừng, khởi động lại và bật/tắt tự khởi động khi boot.
- Xem trạng thái, PID, mức sử dụng bộ nhớ và các dòng log gần đây từ journal.
- Tạo service tùy chỉnh bằng biểu mẫu nhanh hoặc nhập nội dung unit file systemd.
- Xem và chỉnh sửa unit file; có thể yêu cầu khởi động lại service sau khi lưu.
- Xóa service tùy chỉnh và tải lại cấu hình systemd.

> Log được tải khi mở hoặc làm mới cửa sổ log; giao diện hiện không stream log liên tục.

## Yêu cầu

- Máy chủ Linux có `systemd` (`systemctl`).
- aaPanel đã được cài đặt.
- Quyền quản trị/root của aaPanel để thao tác với service và các file trong `/etc/systemd/system/`.
- `journalctl` để xem log.

Plugin này không phải ứng dụng độc lập và không dành cho Windows.

## Cài đặt

### Cách 1: Clone repository

```bash
sudo git clone https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0.git \
  /www/server/panel/plugin/service_manager
```

Chạy script cài đặt:

```bash
sudo bash /www/server/panel/plugin/service_manager/install.sh install
```

### Cách 2: Cài đặt nhanh bằng lệnh tải ZIP

Đăng nhập SSH vào máy chủ aaPanel, sau đó chạy khối lệnh sau bằng tài khoản có quyền `sudo`. Lệnh tải mã nguồn mới nhất từ nhánh `main`, chép các file plugin vào đúng thư mục và chạy script cài đặt:

```bash
sudo bash -c '
set -e
tmp_dir=$(mktemp -d)
trap "rm -rf \"$tmp_dir\"" EXIT
wget -q -O "$tmp_dir/service_manager.zip" "https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0/archive/refs/heads/main.zip"
unzip -q "$tmp_dir/service_manager.zip" -d "$tmp_dir"
install -d /www/server/panel/plugin/service_manager
cp -a "$tmp_dir/Systemd-Service-Manager-1.0-main/." /www/server/panel/plugin/service_manager/
bash /www/server/panel/plugin/service_manager/install.sh install
'
```

Cần có `wget` và `unzip` trên máy chủ. Script `install.sh` hiện chỉ đảm bảo thư mục plugin tồn tại; lệnh trên chủ động chép mã nguồn vào thư mục đó trước khi chạy script. Sau khi cài đặt, tải lại giao diện aaPanel và mở plugin nếu phiên bản/cách cài đặt aaPanel của bạn hỗ trợ nạp plugin từ thư mục này.

Mã Python đã được kiểm tra cú pháp. Script cài đặt được gọi bằng `bash`, nên không cần quyền thực thi riêng.

## Sử dụng

1. Mở **Systemd Service Manager** trong aaPanel.
2. Chọn **Custom Services** hoặc **All System Services**; dùng tìm kiếm và bộ lọc để tìm service.
3. Dùng các thao tác bên cạnh service để điều khiển hoặc xem log.
4. Chọn **Add New Service** để tạo service. Biểu mẫu nhanh cần tên service và lệnh `ExecStart`; có thể tùy chỉnh user, working directory, restart và biến môi trường.
5. Có thể chọn **Raw Unit File** để nhập unit file systemd đầy đủ.

### Lưu ý an toàn

- Thay đổi service có thể làm gián đoạn ứng dụng hoặc máy chủ. Hãy kiểm tra unit file và lệnh trước khi lưu/khởi động lại.
- Xóa service tùy chỉnh sẽ dừng service, tắt tự khởi động và xóa unit file khỏi `/etc/systemd/system/` (cùng file sao lưu `.bak` nếu có). Thao tác này không thể hoàn tác từ plugin.
- Plugin gọi các lệnh hệ thống với quyền của tiến trình aaPanel. Chỉ cài đặt và sử dụng trên máy chủ bạn quản lý.

## Giấy phép

[MIT License](LICENSE)
