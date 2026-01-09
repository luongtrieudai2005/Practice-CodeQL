# Practice-CodeQL

Dự án phân tích bảo mật thư viện **libpng** sử dụng CodeQL để tìm kiếm các lỗ hổng memory leak tiềm năng.

## Cấu trúc thư mục

```
Practice-CodeQL/
├── CodeQL/
│   └── databases/
│       └── libpng-c/              # CodeQL database
│           ├── baseline-info.json
│           ├── codeql-database.yml
│           └── ...
├── my-queries/
│   ├── find_functions.ql          # Query chính
│   ├── qlpack.yml                 # Package configuration
│   ├── codeql-pack.lock.yml       # Dependencies
│   ├── run_query.py               # Script chạy query
│   ├── config.yaml                # File cấu hình (optional)
│   ├── results.csv                # Kết quả cuối cùng
│   └── results_full.csv           # Kết quả đầy đủ từ CodeQL
└── README.md
```

## Cài đặt

### Yêu cầu

- **CodeQL CLI**: [Tải về tại đây](https://github.com/github/codeql-cli-binaries/releases)
- **Python 3.7+**
- **PyYAML** (optional, cho file config): `pip install pyyaml`

### Bước 1: Cài đặt CodeQL CLI

```bash
# Linux/macOS
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH=$PATH:/path/to/codeql

# Windows
# Tải file zip và giải nén
# Thêm đường dẫn vào biến môi trường PATH
```

### Bước 2: Clone repository

```bash
git clone <your-repo-url>
cd Practice-CodeQL
```

### Bước 3: Tạo CodeQL database (nếu chưa có)

```bash
# Tải source code libpng
git clone https://github.com/glennrp/libpng.git

# Tạo database
codeql database create CodeQL/databases/libpng-c \
  --language=cpp \
  --source-root=./libpng \
  --command="make"
```

## Sử dụng

### Cách 1: Chạy đơn giản

```bash
cd my-queries
python3 run_query.py
```

### Cách 2: Với tùy chọn

```bash
# Xem help
python3 run_query.py --help

# Chạy với database khác
python3 run_query.py --database my-other-db

# Chạy query khác
python3 run_query.py --query my_custom_query.ql

# Không xóa cache
python3 run_query.py --no-cache

# Hiển thị thông tin chi tiết
python3 run_query.py --verbose
```

### Cách 3: Sử dụng file config

Tạo file `config.yaml` trong thư mục `my-queries/`:

```yaml
database_name: "libpng-c"
query_file: "find_functions.ql"
output_files:
  full_results: "results_full.csv"
  final_results: "results.csv"
result_columns:
  - index: 0
    name: "Name"
  - index: 4
    name: "Path"
  - index: 3
    name: "Start Line"
preview_lines: 10
```

Sau đó chạy:

```bash
python3 run_query.py
```

## Kết quả

Kết quả sẽ được xuất ra file `results.csv` với format:

| Name | Path | Start Line |
|------|------|------------|
| Potential memory leaks in libpng functions | /png.c | Potential memory leak in function 'png_build_8bit_table': allocation at line 3502 is not freed |
| ... | ... | ... |

## Tùy chỉnh Query

### Chỉnh sửa query hiện tại

Mở file `my-queries/find_functions.ql` và chỉnh sửa:

```ql
// Thêm các hàm allocation khác
class AllocCall extends FunctionCall {
  AllocCall() {
    this.getTarget().getName() = "malloc" or
    this.getTarget().getName() = "calloc" or
    this.getTarget().getName() = "realloc" or
    this.getTarget().getName() = "png_malloc" or
    this.getTarget().getName() = "your_custom_alloc"  // Thêm ở đây
  }
}
```

### Tạo query mới

1. Tạo file `.ql` mới trong thư mục `my-queries/`
2. Chạy với option: `python3 run_query.py --query your_new_query.ql`

## Xử lý lỗi thường gặp

### Lỗi: "codeql not found"

```bash
# Kiểm tra CodeQL đã được cài đặt
codeql --version

# Nếu chưa, thêm vào PATH
export PATH=$PATH:/path/to/codeql
```

### Lỗi: "Database not found"

Đảm bảo cấu trúc thư mục đúng:
```
CodeQL/
└── databases/
    └── libpng-c/
        └── codeql-database.yml
```

### Lỗi: "Query file not found"

Đảm bảo file query tồn tại trong thư mục `my-queries/`