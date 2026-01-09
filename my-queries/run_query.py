import subprocess
import os
import csv

# Xóa cache cũ nếu có
cache_dir = "D:\\PracticeInCodeQL\\CodeQL\\databases\\libpng-c\\results"
if os.path.exists(cache_dir):
    print(f"Đang xóa cache cũ tại {cache_dir}...")
    try:
        import shutil
        shutil.rmtree(cache_dir)
        print("Đã xóa cache thành công!")
    except Exception as e:
        print(f"Không thể xóa cache: {e}")

# Lệnh CodeQL đầy đủ
command = [
    "codeql", "database", "analyze",
    "D:\\PracticeInCodeQL\\CodeQL\\databases\\libpng-c",
    "find_functions.ql",
    "--format=csv",
    "--output=results_full.csv",
    "--rerun"
]

try:
    # Chạy lệnh
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    
    print(f"\n✓ Query đã chạy xong!")
    
    # Đọc file gốc và thêm header
    if os.path.exists("results_full.csv"):
        with open("results_full.csv", "r", encoding="utf-8") as f_in:
            reader = csv.reader(f_in)
            rows = list(reader)
        
        # Tạo file mới với header và chỉ lấy 3 cột cần thiết
        with open("results.csv", "w", encoding="utf-8", newline='') as f_out:
            writer = csv.writer(f_out)
            
            # Viết header
            writer.writerow(["Name", "Path", "Start Line"])
            
            # Viết dữ liệu (lấy cột 0, 3, 4 theo format của CodeQL @kind problem)
            for row in rows:
                if len(row) >= 5:
                    name = row[0]           # Cột 0: Name
                    path = row[4]           # Cột 4: Path  
                    start_line = row[3]     # Cột 3: Start Line
                    writer.writerow([name, path, start_line])
        
        print("✓ File 'results.csv' đã được tạo với header!")
        
        # Hiển thị kết quả
        print("\n--- KẾT QUẢ (results.csv) ---")
        with open("results.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Hiển thị header + 10 dòng đầu
            for line in lines[:11]:
                print(line.rstrip())
            if len(lines) > 11:
                print(f"... và {len(lines) - 11} dòng nữa")
        
        print(f"\n✓ Tổng cộng: {len(lines) - 1} kết quả tìm thấy!")
            
    else:
        print("✗ Không tìm thấy file kết quả!")
        
except subprocess.CalledProcessError as e:
    print(f"\n✗ Lỗi khi chạy lệnh (return code {e.returncode}):")
    print(f"\n--- STDERR ---\n{e.stderr.strip()}")
    if e.stdout.strip():
        print(f"\n--- STDOUT ---\n{e.stdout.strip()}")
except Exception as e:
    print(f"\n✗ Lỗi khác: {str(e)}")