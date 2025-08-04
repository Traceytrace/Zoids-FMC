import importlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from gc_fst import rebuild_iso, extract_iso, gc_fst_exe_path
import shutil
from fpktool import unpack_fpk, pack_fpk
from magictxd import mass_build_txd, mass_export_txd_to_png
import psutil
import json

class WorkspaceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Workspace Manager")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Workspace Manager", 
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=(0, 30))
        
        # Create workspace button
        self.create_btn = ttk.Button(
            self.main_frame,
            text="Create Workspace",
            command=self.create_workspace,
            width=20
        )
        self.create_btn.pack(pady=10)
        
        # Load workspace button
        self.load_btn = ttk.Button(
            self.main_frame,
            text="Load Workspace",
            command=self.load_workspace,
            width=20
        )
        self.load_btn.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="Select an option to get started",
            font=("Arial", 10),
            foreground="gray"
        )
        self.status_label.pack(pady=(30, 0))
        
    def center_window(self):
        """Center the window slightly south of the screen center"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        # Move the window about 1/3 down from the center
        y = (self.root.winfo_screenheight() // 2) - (height // 2) + (self.root.winfo_screenheight() // 6)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_workspace(self):
        """Handle create workspace button click"""
        try:
            # Ask user to select a directory for the new workspace
            workspace_dir = filedialog.askdirectory(
                title="Select Directory for New Workspace",
                initialdir=os.path.expanduser("~")
            )
            
            # Ask user to select a directory for the new workspace
            iso_file = filedialog.askopenfilename(
                title="Select ISO File",
                initialdir=os.path.expanduser("~"),
                filetypes=[("ISO Files", "*.iso")]
            )

            if workspace_dir and iso_file:
                os.chdir(workspace_dir)
                print(f"Creating workspace in: {workspace_dir}")
                # Create workspace structure
                workspace_name = os.path.basename(workspace_dir)
                if not workspace_name:
                    workspace_name = "new_workspace"
                print(f"Workspace name: {workspace_name}")
                # Copy gc_fst_exe to workspace directory
                new_gc_fst_exe = os.path.join(workspace_dir, "gc_fst.exe")
                shutil.copy(gc_fst_exe_path, new_gc_fst_exe)
                print(f"Copied gc_fst_exe to: {new_gc_fst_exe}")
                extract_iso(exe_path=new_gc_fst_exe, iso_path=iso_file)

                if not os.path.isdir(os.path.join(workspace_dir, "root")):
                    raise FileNotFoundError(f"Selected workspace directory does not exist: {workspace_dir}")
                
                # Create subdirectories
                subdirs = ["root_unpacked_fpk", "root_unpacked_txd", "config_folder", "font_presets"]
                for subdir in subdirs:
                    os.makedirs(os.path.join(workspace_dir, subdir), exist_ok=True)
                
                # unpack all fpk files in the root directory
                root_dir = os.path.join(workspace_dir, "root")
                root_unpacked_fpk_dir = os.path.join(workspace_dir, "root_unpacked_fpk")
                # Recursively unpack all .fpk files in root_dir and its subdirectories
                for dirpath, _, filenames in os.walk(root_dir):
                    for fpk_file in filenames:
                        if fpk_file.endswith('.fpk'):
                            fpk_path = os.path.join(dirpath, fpk_file)
                            fpk_filename = os.path.basename(fpk_path)
                            # Preserve directory structure in output
                            rel_dir = os.path.relpath(dirpath, root_dir)
                            output_dir = os.path.join(root_unpacked_fpk_dir, rel_dir)
                            os.makedirs(output_dir, exist_ok=True)
                            unpack_fpk(input_file=fpk_path, output_folder=os.path.join(output_dir, fpk_filename[:-4]))

                # unpack all txd files in the root directory
                root_unpacked_txd_dir = os.path.join(workspace_dir, "root_unpacked_txd")
                mass_export_txd_to_png(root_unpacked_fpk_dir, root_unpacked_txd_dir, click_export_button=True)


                # Check if magic.txd process is running
                def is_magic_txd_running():
                    return any(
                        "magictxd.exe" in (p.name() or "").lower() or "magic_txd" in (p.name() or "").lower()
                        for p in psutil.process_iter(['name'])
                    )

                while is_magic_txd_running():
                    messagebox.showwarning(
                        "Warning",
                        "Batch export still running.\nWait for it to finish.\nWhen done, close Magic TXD and click OK"
                    )

                ##########################################################################################
                # fix up directory structure for story files
                #
                # Walk through the story_folder and process every file in it and its subdirectories
                for dirpath, _, filenames in os.walk(root_unpacked_txd_dir):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        if filename.endswith(".png.png"):
                            new_file_path = os.path.join(dirpath, filename[:-4])  # Remove the last ".png"
                            os.rename(file_path, new_file_path)

                # create translation index file
                fpk_files = []
                for root, dirs, files in os.walk(root_dir):
                    for file in files:
                        if file.lower().endswith('.fpk'):
                            fpk_files.append(os.path.join(root, file))
                rel_paths = []
                for f in fpk_files:
                    rel_path = os.path.relpath(f, root_dir)
                    rel_paths.append(rel_path[:-4])
                
                png_file_paths = []
                for rel_path in rel_paths:
                    folder_path = os.path.join(root_unpacked_txd_dir, rel_path)
                    #print(f"Checking folder: {folder_path}")
                    if os.path.isdir(folder_path):
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                if file.lower().endswith('.png'):
                                    rel_path = os.path.relpath(root, root_unpacked_txd_dir)
                                    png_file_paths.append(os.path.join(rel_path, file))
                # Use the list you want as keys, e.g., png_file_paths
                keys_list = png_file_paths  # or rel_paths, txd_file_paths, etc.

                json_dict = {k: None for k in keys_list}

                with open("translation_index.json", "w", encoding="utf-8") as f:
                    json.dump(json_dict, f, indent=2, ensure_ascii=False)


                # Create a simple config file
                config_file = os.path.join(workspace_dir, "workspace.config")
                with open(config_file, 'w') as f:
                    f.write(f"workspace_name={workspace_name}\n")
                
                self.status_label.config(
                    text=f"Workspace created: {workspace_name}",
                    foreground="green"
                )
                
                if messagebox.askyesno(
                    "Open Workspace?",
                    f"Workspace '{workspace_name}' created successfully!\n\nLocation: {workspace_dir}\nWould you like to open the workspace now?"
                ):
                    self.open_main_application(workspace_dir)
                
        except Exception as e:
            self.status_label.config(
                text="Error creating workspace",
                foreground="red"
            )
            messagebox.showerror("Error", f"Failed to create workspace:\n{str(e)}")
    
    def load_workspace(self):
        """Handle load workspace button click"""
        try:
            # Ask user to select a workspace directory
            workspace_dir = filedialog.askdirectory(
                title="Select Workspace Directory",
                initialdir=os.path.expanduser("~")
            )
            
            if workspace_dir:
                # Check if it's a valid workspace (has config file)
                config_file = os.path.join(workspace_dir, "workspace.config")
                
                if os.path.exists(config_file):
                    # Read workspace config
                    workspace_name = os.path.basename(workspace_dir)
                    
                    self.status_label.config(
                        text=f"Workspace loaded: {workspace_name}",
                        foreground="green"
                    )
                    
                    messagebox.showinfo(
                        "Success", 
                        f"Workspace '{workspace_name}' loaded successfully!\n\nLocation: {workspace_dir}"
                    )
                    
                    # Here you could open your main application window
                    self.open_main_application(workspace_dir)
                    
                else:
                    self.status_label.config(
                        text="Invalid workspace selected",
                        foreground="red"
                    )
                    messagebox.showwarning(
                        "Invalid Workspace", 
                        "The selected directory is not a valid workspace.\n\nPlease select a directory that contains a workspace.config file."
                    )
                    
        except Exception as e:
            self.status_label.config(
                text="Error loading workspace",
                foreground="red"
            )
            messagebox.showerror("Error", f"Failed to load workspace:\n{str(e)}")
    
    def open_main_application(self, workspace_dir):
        """Open the main application with the loaded workspace"""
        # This is where you would launch your main application
        # For now, just print the workspace directory
        print(f"Opening main application with workspace: {workspace_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkspaceManager(root)
    root.mainloop()