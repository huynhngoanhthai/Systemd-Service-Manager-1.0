# Systemd Service Manager

Plugin tiện ích dành riêng cho **aaPanel** giúp quản lý toàn diện các `systemd` service trên máy chủ Linux trực tiếp từ giao diện web trực quan.

[English](README.md) | [Tiếng Việt](README_VI.md)

---

## 📸 Giao diện ứng dụng (Screenshots)

### 1. Quản lý Service tùy chỉnh (Custom Services)
Quản lý tập trung các dịch vụ do bạn tự tạo hoặc thêm vào hệ thống với đầy đủ các thao tác: Bật/Tắt, Khởi động lại, Xem log, Sửa cấu hình và Xóa.

![Quản lý Custom Services](screenshots/custom_services.png)

### 2. Quản lý toàn bộ Service hệ thống (All System Services)
Theo dõi trạng thái của hơn 200+ dịch vụ hệ thống Linux (Docker, Cron, Nginx, SSHD,...), hỗ trợ tìm kiếm mượt mà và nút **Daemon Reload** tiện lợi.

![Quản lý All System Services](screenshots/all_system_services.png)

---

## 🌟 Tính năng nổi bật

- **Xem danh sách trực quan:** Theo dõi trạng thái hoạt động (Running, Stopped, Exited, Failed) và trạng thái khởi động cùng hệ điều hành (Enabled / Disabled at boot).
- **Phân tách thông minh:** Phân loại rõ ràng giữa dịch vụ người dùng tạo (**Custom Services**) và dịch vụ hệ thống (**All System Services**) để tránh thao tác nhầm.
- **Điều khiển tức thì:** Khởi động (Start), Dừng (Stop), Khởi động lại (Restart), Tự động chạy khi boot (Enable/Disable).
- **Tạo Service linh hoạt với 2 chế độ:**
  - **Quick Form:** Điền form nhanh cho các ứng dụng phổ biến (Node.js, Python, Go, Java, script bash,...).
  - **Raw Unit File:** Tự do soạn thảo file unit `.service` đầy đủ với các tham số chuyên sâu.
- **Xem Log & Giám sát:** Tra cứu thông tin PID, RAM tiêu thụ và xem nhanh các dòng log mới nhất trích xuất trực tiếp từ `journalctl`.
- **An toàn & Tiện lợi:** Hỗ trợ tính năng sao lưu file `.bak` khi chỉnh sửa, tự động chạy `systemctl daemon-reload` sau khi thay đổi cấu hình.

---

## 📋 Yêu cầu hệ thống

- Máy chủ Linux sử dụng hệ thống init `systemd` (hỗ trợ lệnh `systemctl`).
- Đã cài đặt **aaPanel**.
- Tài khoản chạy aaPanel có quyền `root` / quản trị để thao tác với các tệp tin trong `/etc/systemd/system/`.
- Tiện ích `journalctl` để đọc nhật ký log hệ thống.

---

## 🚀 Hướng dẫn cài đặt

### Cách 1: Clone từ GitHub (Khuyên dùng)

Đăng nhập SSH vào máy chủ Linux và chạy lệnh:

```bash
sudo git clone https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0.git \
  /www/server/panel/plugin/service_manager
```

Kích hoạt cài đặt plugin:

```bash
sudo bash /www/server/panel/plugin/service_manager/install.sh install
```

---

### Cách 2: Cài đặt nhanh bằng 1 câu lệnh (Không cần git)

Chạy khối lệnh sau trong Terminal máy chủ để tự động tải bản nén ZIP mới nhất từ nhánh `main` và cài đặt:

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

*Lưu ý: Máy chủ cần cài sẵn gói `wget` và `unzip` (`yum install -y wget unzip` hoặc `apt install -y wget unzip`). Sau khi cài đặt thành công, nhấn `F5` tải lại trang web aaPanel để thấy icon plugin trong mục **App Store**.*

---

## 📖 Hướng dẫn sử dụng chi tiết

### 1. Quản lý và vận hành Service

- **Tìm kiếm:** Nhập tên dịch vụ vào ô tìm kiếm ở góc phải và bấm **Search** (hoặc nhấn phím Enter).
- **Lọc trạng thái:** Sử dụng menu dropdown **All Statuses** để lọc nhanh các dịch vụ đang chạy (`Running`), đã dừng (`Stopped`),...
- **Thao tác nhanh:**
  - Bấm **Start** / **Stop** / **Restart** để điều khiển tiến trình.
  - Bấm **Logs** để kiểm tra log hoạt động gần nhất nếu dịch vụ bị lỗi hoặc muốn theo dõi tiến trình.
  - Bấm **Edit** để chỉnh sửa lại nội dung file `.service`.
  - Bấm **Daemon Reload** ở thanh công cụ phía trên bất cứ khi nào bạn thay đổi cấu hình service ngoài console SSH.

---

### 2. Tạo Service mới

Nhấp vào nút màu xanh **+ Add New Service** ở góc trái giao diện:

#### Chế độ 1: Tạo nhanh (Quick Form)
Phù hợp với hầu hết nhu cầu chạy ứng dụng web (Node.js, Python FastAPI/Flask/Django, Go, Java, script nền,...).

![Tạo Service nhanh](screenshots/add_service_quick_form.png)

1. **Service Name:** Nhập tên dịch vụ (ví dụ: `my-web-app`). Plugin sẽ tự động thêm đuôi `.service` nếu bạn chưa nhập.
2. **Exec Command:** Đường dẫn lệnh thực thi ứng dụng (ví dụ: `/usr/bin/node /www/wwwroot/my-app/app.js` hoặc `/usr/bin/python3 /www/wwwroot/api/main.py`).
3. **Working Directory:** Thư mục gốc chứa source code của ứng dụng (ví dụ: `/www/wwwroot/my-app`).
4. **User / Restart:** Chọn quyền chạy (mặc định: `root` hoặc user khác như `www`) và cơ chế khởi động lại (khuyên dùng: `Restart: Always` để tự chạy lại khi ứng dụng bị crash).
5. **Environment Vars:** Biến môi trường dạng `KEY=VALUE` (phân cách bằng khoảng trắng hoặc xuống dòng), ví dụ: `PORT=3000 NODE_ENV=production`.
6. Tích chọn **Enable at Boot** (tự khởi động khi bật máy chủ) và **Start immediately after creation** (khởi động ngay sau khi tạo).
7. Nhấn **Create Service** để hoàn tất.

---

#### Chế độ 2: Tự soạn thảo cấu hình (Raw Unit File)
Dành cho người dùng có kinh nghiệm cần tùy biến chuyên sâu các directive của systemd (`Type=forking`, `After=network.target mysql.service`, `StandardOutput`, giới hạn `LimitNOFILE`,...).

![Tạo Service Raw Unit](screenshots/add_service_raw_unit.png)

1. Nhập tên service tại ô **Service Name**.
2. Soạn thảo hoặc dán nội dung unit file hoàn chỉnh vào khung code.
3. Tùy chọn bật tự khởi động cùng hệ thống và chạy ngay.
4. Bấm **Create Service**.

---

## 🗑️ Hướng dẫn gỡ cài đặt (Khi không cần sử dụng)

Khi bạn không còn nhu cầu sử dụng plugin **Systemd Service Manager**, bạn có thể gỡ bỏ dễ dàng theo một trong các cách sau:

### Cách 1: Gỡ qua giao diện aaPanel
1. Mở trang quản trị **aaPanel**.
2. Vào mục **App Store** (Cửa hàng ứng dụng) -> chọn tab **Installed** (Đã cài đặt).
3. Tìm tiện ích **Systemd Service Manager**.
4. Nhấn nút **Uninstall** (Gỡ cài đặt) và xác nhận.

---

### Cách 2: Gỡ qua dòng lệnh Terminal / SSH
Đăng nhập SSH vào máy chủ và thực thi lệnh gỡ cài đặt chính thức của plugin:

```bash
sudo bash /www/server/panel/plugin/service_manager/install.sh uninstall
```

Hoặc xóa trực tiếp thư mục plugin nếu muốn dọn sạch nhanh:

```bash
sudo rm -rf /www/server/panel/plugin/service_manager
```

> **Lưu ý an toàn khi gỡ:**  
> Việc gỡ bỏ plugin chỉ xóa giao diện quản lý trên aaPanel. Mọi service mà bạn đã tạo trong `/etc/systemd/system/` **vẫn sẽ tiếp tục chạy bình thường** trên máy chủ Linux mà không bị mất đi hay gián đoạn, trừ khi bạn đã chủ động bấm nút **Delete** xóa service đó trước khi gỡ plugin.

---

## ⚠️ Lưu ý an toàn

- Việc dừng hoặc thay đổi cấu hình các service quan trọng của hệ thống (như `network`, `sshd`, `mysql`, `nginx`,...) có thể làm mất kết nối hoặc ảnh hưởng đến sự ổn định của máy chủ. Hãy cẩn trọng trước khi thực hiện.
- Thao tác **Delete** đối với Custom Service sẽ lập tức dừng dịch vụ, tắt tự khởi động và xóa vĩnh viễn file `.service` khỏi `/etc/systemd/system/`. Thao tác này không thể hoàn tác từ plugin.

---

## 📄 Giấy phép

Phát hành theo [Giấy phép MIT](LICENSE).
