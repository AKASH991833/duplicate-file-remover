# Run this script to create test duplicate files
import os
import shutil

# Create test folder
test_folder = "test_files"
os.makedirs(test_folder, exist_ok=True)

# Create some duplicate files
content = b"This is a test file content. Same content means duplicate."

for i in range(5):
    with open(os.path.join(test_folder, f"file{i}.txt"), "wb") as f:
        f.write(content)

print(f"Created 5 duplicate files in {test_folder}")
print("Now run main.py and scan this folder!")