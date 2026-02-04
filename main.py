import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import shutil
from datetime import datetime
from file_scanner import FileScanner
import threading

class DuplicateFileRemover:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("Duplicate File Remover")
        self.root.geometry("1000x700")
        
        # Variables
        self.selected_folder = ""
        self.duplicates = {}
        self.selected_files = set()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="🧹 DUPLICATE FILE REMOVER",
            font=("Arial", 18, "bold"),
            fg="blue"
        )
        title_label.pack(pady=10)
        
        # Folder selection frame
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            folder_frame,
            text="Select Folder to Scan:",
            font=("Arial", 11)
        ).pack(side="left")
        
        self.folder_entry = tk.Entry(
            folder_frame,
            width=60,
            font=("Arial", 10)
        )
        self.folder_entry.pack(side="left", padx=10)
        
        browse_btn = tk.Button(
            folder_frame,
            text="📁 Browse",
            command=self.browse_folder,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        )
        browse_btn.pack(side="left")
        
        # Scan button
        scan_btn = tk.Button(
            self.root,
            text="🔍 START SCAN",
            command=self.start_scan_thread,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10
        )
        scan_btn.pack(pady=10)
        
        # Progress frame
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=5, padx=20, fill="x")
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Ready to scan...",
            font=("Arial", 10)
        )
        self.progress_label.pack(side="left")
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=300,
            mode='indeterminate'
        )
        self.progress_bar.pack(side="right")
        
        # Results area
        results_frame = tk.LabelFrame(
            self.root,
            text="Duplicate Files Found",
            font=("Arial", 11, "bold")
        )
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Create Treeview with scrollbars
        tree_frame = tk.Frame(results_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Select", "File Path", "Size", "Modified"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="none"
        )
        
        # Configure columns
        self.tree.heading("Select", text="✓")
        self.tree.heading("File Path", text="File Path")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Modified", text="Last Modified")
        
        self.tree.column("Select", width=50, anchor="center")
        self.tree.column("File Path", width=400)
        self.tree.column("Size", width=100, anchor="center")
        self.tree.column("Modified", width=150, anchor="center")
        
        # Pack everything
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Bind checkbox click
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Action buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.delete_btn = tk.Button(
            button_frame,
            text="🗑️ DELETE SELECTED",
            command=self.delete_selected,
            bg="#FF5722",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=10)
        
        self.select_all_btn = tk.Button(
            button_frame,
            text="✓ SELECT ALL",
            command=self.select_all_duplicates,
            bg="#607D8B",
            fg="white",
            font=("Arial", 11),
            padx=20
        )
        self.select_all_btn.pack(side="left", padx=10)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🔄 CLEAR ALL",
            command=self.clear_selection,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 11),
            padx=20
        )
        self.clear_btn.pack(side="left", padx=10)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_folder = folder_selected
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)
            self.status_bar.config(text=f"Selected: {folder_selected}")
    
    def start_scan_thread(self):
        if not self.selected_folder or not os.path.exists(self.selected_folder):
            messagebox.showwarning("Warning", "Please select a valid folder first!")
            return
        
        # Disable buttons during scan
        self.progress_bar.start()
        self.progress_label.config(text="Scanning... Please wait")
        self.delete_btn.config(state="disabled")
        
        # Run scan in separate thread
        scan_thread = threading.Thread(target=self.perform_scan)
        scan_thread.daemon = True
        scan_thread.start()
    
    def perform_scan(self):
        try:
            scanner = FileScanner()
            self.duplicates = scanner.scan_folder(self.selected_folder)
            
            # Update UI in main thread
            self.root.after(0, self.display_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        
        finally:
            self.root.after(0, self.scan_complete)
    
    def display_results(self):
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Display duplicates
        if not self.duplicates:
            messagebox.showinfo("No Duplicates", "No duplicate files found!")
            return
        
        group_count = 0
        total_duplicates = 0
        
        for hash_value, file_list in self.duplicates.items():
            group_count += 1
            
            # Add group separator (only show duplicates, not the original)
            duplicate_count = len(file_list) - 1
            if duplicate_count > 0:
                self.tree.insert("", "end", values=(
                    "",
                    f"────── GROUP {group_count}: {duplicate_count} duplicate files ──────",
                    "",
                    ""
                ), tags=("group",))
                
                # Add only duplicate files in this group (skip the first/original)
                for i, file_path in enumerate(file_list):
                    if i == 0:
                        continue  # Skip the original file
                    
                    try:
                        file_info = FileScanner().get_file_info(file_path)
                        if file_info:
                            # All shown files are duplicates to delete
                            checkbox = "□"
                            
                            self.tree.insert("", "end", values=(
                                checkbox,
                                file_path,
                                file_info['size_readable'],
                                file_info['modified'].strftime("%Y-%m-%d %H:%M")
                            ), tags=("file",))
                            
                            total_duplicates += 1
                    except:
                        continue
        
        # Update status
        self.status_bar.config(text=f"Found {total_duplicates} duplicate files in {group_count} groups")
        self.progress_label.config(text=f"Found {group_count} duplicate groups")
        
        # Enable delete button
        self.delete_btn.config(state="normal")
    
    def scan_complete(self):
        self.progress_bar.stop()
        self.progress_label.config(text="Scan completed!")
    
    def on_tree_click(self, event):
        # Handle checkbox clicks
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "cell":
            item = self.tree.identify_row(event.y)
            values = self.tree.item(item, "values")
            if values and values[0] in ["□", "✓"]:
                # Toggle checkbox
                new_value = "✓" if values[0] == "□" else "□"
                new_values = list(values)
                new_values[0] = new_value
                self.tree.item(item, values=tuple(new_values))
                
                # Update selected files set
                file_path = values[1]
                if new_value == "✓":
                    self.selected_files.add(file_path)
                else:
                    self.selected_files.discard(file_path)
                
                # Update status
                self.status_bar.config(text=f"{len(self.selected_files)} file(s) selected for deletion")
    
    def select_all_duplicates(self):
        self.selected_files.clear()
        
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values and values[0] == "□":
                # Only select files with empty checkbox (not the first in group)
                new_values = list(values)
                new_values[0] = "✓"
                self.tree.item(item, values=tuple(new_values))
                
                # Add to selected set
                self.selected_files.add(values[1])
        
        self.status_bar.config(text=f"{len(self.selected_files)} file(s) selected for deletion")
    
    def clear_selection(self):
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values and values[0] == "✓":
                new_values = list(values)
                new_values[0] = "□"
                self.tree.item(item, values=tuple(new_values))
        
        self.selected_files.clear()
        self.status_bar.config(text="Selection cleared")
    
    def delete_selected(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "No files selected for deletion!")
            return
        
        # Confirm deletion
        deleted_folder = os.path.join(self.selected_folder, "Deleted_Duplicates")
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(self.selected_files)} file(s)?\n\n"
            f"Files will be moved to: {deleted_folder}"
        )
        
        if not confirm:
            return
        
        # Create deleted folder if not exists
        os.makedirs(deleted_folder, exist_ok=True)
        
        deleted_count = 0
        errors = []
        
        for file_path in self.selected_files:
            try:
                # Move file to deleted folder
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(deleted_folder, file_name)
                
                # If file already exists in deleted folder, add number
                counter = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(file_name)
                    dest_path = os.path.join(deleted_folder, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.move(file_path, dest_path)
                
                deleted_count += 1
                
                # Remove from tree
                for item in self.tree.get_children():
                    values = self.tree.item(item, "values")
                    if values and values[1] == file_path:
                        self.tree.delete(item)
                        break
                        
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Show results
        if errors:
            messagebox.showwarning(
                "Partial Success",
                f"Deleted {deleted_count} file(s)\n\n"
                f"Failed to delete {len(errors)} file(s):\n" + "\n".join(errors[:5])
            )
        else:
            messagebox.showinfo("Success", f"Successfully deleted {deleted_count} file(s)")
        
        self.selected_files.clear()
        self.status_bar.config(text=f"Deleted {deleted_count} file(s)")
    
    def run(self):
        self.root.mainloop()

# Main entry point
if __name__ == "__main__":
    print("=" * 60)
    print("DUPLICATE FILE REMOVER")
    print("=" * 60)
    print("Starting application...")
    
    app = DuplicateFileRemover()
    app.run()