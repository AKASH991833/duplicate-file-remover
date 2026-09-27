# Duplicate File Remover

A Python/Tkinter desktop app for scanning a folder, finding files with matching content and choosing which copies to move out of the way.

## How it works

1. Select a folder to scan.
2. The scanner groups files by size and then compares MD5 hashes for possible duplicates.
3. Review the duplicate groups and select the copies you want to remove.
4. Selected files are moved to a `Deleted_Duplicates` folder inside the scanned folder. Review this folder before permanently deleting anything.

## Run locally

```bash
python -m pip install -r requirements.txt
python main.py
```

The app uses Python's Tkinter GUI. `requirements.txt` lists `winshell`, `send2trash` and `Pillow`; check that your environment supports the packages before installation.

## Files

- `main.py` - GUI and selected-file handling
- `file_scanner.py` - file-size grouping and MD5 hashing
- `requirements.txt` - listed dependencies

**Note:** MD5 is used here to group likely duplicate files; it is not a secure integrity check. Back up important files before moving or deleting them.
