import os
import hashlib
from collections import defaultdict
import time
from datetime import datetime

class FileScanner:
    def __init__(self):
        self.total_files = 0
        self.scanned_files = 0
        
    def find_duplicates_by_size(self, folder_path):
        """First pass: Group files by size (fast)"""
        size_dict = defaultdict(list)
        
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                self.total_files += 1
                full_path = os.path.join(root, filename)
                
                try:
                    file_size = os.path.getsize(full_path)
                    size_dict[file_size].append(full_path)
                except (OSError, PermissionError):
                    continue
        
        # Return only groups with same size (potential duplicates)
        potential_duplicates = {size: paths for size, paths in size_dict.items() if len(paths) > 1}
        return potential_duplicates
    
    def find_duplicates_by_hash(self, file_list):
        """Second pass: Check hash for files with same size"""
        hash_dict = defaultdict(list)
        
        for filepath in file_list:
            try:
                file_hash = self.calculate_file_hash(filepath)
                hash_dict[file_hash].append(filepath)
                self.scanned_files += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue
        
        # Return only actual duplicates (same hash)
        actual_duplicates = {hash_val: paths for hash_val, paths in hash_dict.items() if len(paths) > 1}
        return actual_duplicates
    
    def calculate_file_hash(self, filepath, chunk_size=8192):
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def get_file_info(self, filepath):
        """Get file information"""
        try:
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'size_readable': self.convert_size(stat.st_size)
            }
        except:
            return None
    
    def convert_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ("B", "KB", "MB", "GB")
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def scan_folder(self, folder_path):
        """Main scanning function"""
        print(f"Starting scan of: {folder_path}")
        print("-" * 50)
        
        start_time = time.time()
        
        # Step 1: Find files with same size
        print("Step 1: Grouping files by size...")
        size_groups = self.find_duplicates_by_size(folder_path)
        print(f"Found {len(size_groups)} groups of files with same size")
        
        # Step 2: Check hash for each size group
        print("\nStep 2: Checking file content (MD5 hash)...")
        all_duplicates = {}
        
        for size, files in size_groups.items():
            hash_groups = self.find_duplicates_by_hash(files)
            all_duplicates.update(hash_groups)
        
        end_time = time.time()
        
        # Print summary
        print("-" * 50)
        print("SCAN COMPLETED!")
        print(f"Total files found: {self.total_files}")
        print(f"Files scanned: {self.scanned_files}")
        print(f"Duplicate groups found: {len(all_duplicates)}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
        return all_duplicates