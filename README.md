# Inventory Expiry Analytics Lab

## Chạy trên Windows

Giải nén ZIP. Trong File Explorer, mở thư mục chứa `run_inventory.py`, gõ `powershell` vào thanh địa chỉ rồi nhấn Enter. Cần Python 3.12 và mạng lần cài đầu.

```powershell
Get-Location
Get-ChildItem
python src/prepare_data.py
python src/analyze.py
python run_inventory.py --notebook
```

`Get-Location` cho biết thư mục hiện tại và `Get-ChildItem` liệt kê tệp. Nếu thiếu `run_inventory.py`, dùng `cd "đường dẫn thư mục dự án"` rồi thử lại. Lệnh chuẩn bị tạo SQLite và xuất CSV nguồn vào `data/raw`. Lệnh phân tích ghi báo cáo, CSV và PNG vào `outputs`. Launcher mở bài `notebooks/02_analysis.ipynb`. Nếu Jupyter hiện tab **Running**, chọn **Files** rồi mở bài. Nhấn **Shift+Enter** từng ô từ trên xuống.

`python run_inventory.py` mở menu. Nhấp đúp `START_WINDOWS.cmd` hoặc `START_NOTEBOOK.cmd` cũng được. Trong menu nhập số lựa chọn. Viết SQL trong ô notebook.

## Bắt đầu với FEFO

Với hai lô còn 8 và 10 hộp, hết hạn lần lượt vào ngày 10 và 20, yêu cầu 12 hộp phân thành 8 + 4 khi cả hai còn hạn. Sau ngày 10, lô đầu vẫn nằm trong tồn vật lý. Mô phỏng lấy 10 từ lô thứ hai và báo thiếu 2. Mỗi lô còn đủ điều kiện đến hết ngày ghi hạn. Báo cáo cận hạn xét từ hôm nay đến hết ngày thứ 7.

```powershell
python src/analyze.py --as-of 2026-02-15 --out outputs/february
python src/prepare_data.py --db database/practice.db
python run_inventory.py --notebook --db database/practice.db
git log --oneline
git show <mã-commit>
```

`--as-of` chọn ngày quan sát trong quý I/2026, mặc định 31/03. `--db` chọn bản thực hành riêng, `--out` chọn thư mục kết quả. `python -m` chạy module Python. Git dùng để xem 12 bước phát triển. Thay `<mã-commit>` bằng mã ở đầu dòng trong `git log`.

Dữ liệu giả lập, giờ Việt Nam. Menu và notebook mở SQLite chỉ đọc. Mã nguồn MIT.

Đọc [từ điển và sơ đồ dữ liệu](docs/data_dictionary.md), chạy notebook tổng hợp rồi xem [20 bài tập](docs/exercises.md) và [lời giải](docs/solutions.md). Workflow phân tích trên GitHub giữ báo cáo và notebook đã chạy 14 ngày.
