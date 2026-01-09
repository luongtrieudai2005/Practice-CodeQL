import subprocess
import os
import csv
import sys
import argparse
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Cấu hình mặc định
DEFAULT_CONFIG = {
    'database_name': 'libpng-c',
    'query_file': 'find_functions.ql',
    'output_files': {
        'full_results': 'results_full.csv',
        'final_results': 'results.csv'
    },
    'result_columns': [
        {'index': 0, 'name': 'Name'},
        {'index': 4, 'name': 'Path'},
        {'index': 3, 'name': 'Start Line'}
    ],
    'preview_lines': 10
}

def load_config():
    """Load cấu hình từ file hoặc dùng mặc định"""
    script_dir = Path(__file__).resolve().parent
    config_file = script_dir / "config.yaml"
    
    if HAS_YAML and config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"[INFO] Đã load config từ: {config_file}")
                return config
        except Exception as e:
            print(f"[WARNING] Lỗi khi đọc config.yaml: {e}")
            print("          Sử dụng cấu hình mặc định...")
    
    return DEFAULT_CONFIG

def get_project_root():
    """Tự động tìm thư mục gốc của project"""
    current = Path(__file__).resolve().parent
    # Tìm thư mục chứa CodeQL/databases
    while current != current.parent:
        if (current / "CodeQL" / "databases").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

def find_database_path(db_name):
    """Tìm đường dẫn database tự động"""
    project_root = get_project_root()
    db_dir = project_root / "CodeQL" / "databases"
    
    if not db_dir.exists():
        print(f"[ERROR] Không tìm thấy thư mục databases tại: {db_dir}")
        print("        Hãy đảm bảo cấu trúc thư mục:")
        print("        - CodeQL/databases/{database_name}/")
        sys.exit(1)
    
    # Tìm database
    target_db = db_dir / db_name
    if target_db.exists():
        return target_db
    
    # Nếu không tìm thấy, liệt kê các database có sẵn
    available_dbs = [d.name for d in db_dir.iterdir() if d.is_dir()]
    if available_dbs:
        print(f"[ERROR] Không tìm thấy database '{db_name}'")
        print(f"        Các database có sẵn: {available_dbs}")
        sys.exit(1)
    else:
        print(f"[ERROR] Không có database nào trong {db_dir}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Chạy CodeQL query trên database')
    parser.add_argument('--database', '-d', help='Tên database (ghi đè config)')
    parser.add_argument('--query', '-q', help='File query (ghi đè config)')
    parser.add_argument('--no-cache', action='store_true', help='Không xóa cache cũ')
    parser.add_argument('--verbose', '-v', action='store_true', help='Hiển thị thông tin chi tiết')
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    
    # Override từ command line
    db_name = args.database or config['database_name']
    query_filename = args.query or config['query_file']
    
    # Lấy đường dẫn động
    script_dir = Path(__file__).resolve().parent
    database_path = find_database_path(db_name)
    query_file = script_dir / query_filename
    
    output_config = config['output_files']
    results_full = script_dir / output_config['full_results']
    results_final = script_dir / output_config['final_results']
    cache_dir = database_path / "results"
    
    # Hiển thị thông tin
    print("=" * 70)
    print("CODEQL QUERY RUNNER")
    print("=" * 70)
    print(f"Thư mục script: {script_dir}")
    print(f"Database: {database_path}")
    print(f"Query file: {query_file}")
    print(f"Output: {results_final}")
    print("=" * 70 + "\n")
    
    # Kiểm tra query file tồn tại
    if not query_file.exists():
        print(f"[ERROR] Không tìm thấy file query: {query_file}")
        sys.exit(1)
    
    # Xóa cache cũ nếu có
    if not args.no_cache and cache_dir.exists():
        print(f"[INFO] Đang xóa cache cũ tại {cache_dir}...")
        try:
            import shutil
            shutil.rmtree(cache_dir)
            print("[INFO] Đã xóa cache thành công!\n")
        except Exception as e:
            print(f"[WARNING] Không thể xóa cache: {e}\n")
    
    # Lệnh CodeQL với đường dẫn tương đối
    command = [
        "codeql", "database", "analyze",
        str(database_path),
        str(query_file),
        "--format=csv",
        f"--output={results_full}",
        "--rerun"
    ]
    
    print(f"[INFO] Đang chạy CodeQL query...")
    if args.verbose:
        print(f"       Command: {' '.join(command)}\n")
    
    try:
        # Chạy lệnh
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True,
            cwd=str(script_dir)
        )
        
        if args.verbose and result.stdout:
            print(result.stdout)
        
        print(f"[INFO] Query đã chạy xong!\n")
        
        # Đọc file gốc và thêm header
        if results_full.exists():
            with open(results_full, "r", encoding="utf-8") as f_in:
                reader = csv.reader(f_in)
                rows = list(reader)
            
            # Tạo file mới với header
            with open(results_final, "w", encoding="utf-8", newline='') as f_out:
                writer = csv.writer(f_out)
                
                # Viết header từ config
                column_config = config['result_columns']
                headers = [col['name'] for col in column_config]
                writer.writerow(headers)
                
                # Viết dữ liệu theo config
                for row in rows:
                    if len(row) >= max(col['index'] for col in column_config) + 1:
                        data_row = [row[col['index']] for col in column_config]
                        writer.writerow(data_row)
            
            print(f"[INFO] File '{results_final.name}' đã được tạo!\n")
            
            # Hiển thị kết quả
            print("=" * 70)
            print("KET QUA")
            print("=" * 70)
            with open(results_final, "r", encoding="utf-8") as f:
                lines = f.readlines()
                preview_lines = config.get('preview_lines', 10)
                
                # Hiển thị header + n dòng đầu
                for line in lines[:preview_lines + 1]:
                    print(line.rstrip())
                
                if len(lines) > preview_lines + 1:
                    print(f"\n... và {len(lines) - preview_lines - 1} dòng nữa")
            
            print("\n" + "=" * 70)
            print(f"[SUCCESS] Tổng cộng: {len(lines) - 1} kết quả tìm thấy!")
            print(f"[INFO] Kết quả đầy đủ: {results_final}")
            print("=" * 70)
                
        else:
            print("[ERROR] Không tìm thấy file kết quả!")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Lỗi khi chạy CodeQL (return code {e.returncode}):")
        print(f"\n--- STDERR ---")
        print(e.stderr.strip())
        if e.stdout.strip():
            print(f"\n--- STDOUT ---")
            print(e.stdout.strip())
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Lỗi: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()