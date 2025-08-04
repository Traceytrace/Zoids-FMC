import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os
from imagetools import detect_bounding_boxes, draw_bounding_boxes, erase_bounding_boxes, write_onto_png, get_available_fonts, convert_png_to_P
from magictxd import mass_build_txd
import json
import shutil
import pyperclip
import easyocr
import numpy as np
from tkinter import filedialog, messagebox
from datetime import datetime
import psutil

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Template with Sidebar")
        self.root.geometry("1200x900")  # Changed to 1200x900
        self.workspace_directory = "C:/Users/nickf/Documents/Zoids_FMC/Translator workspace"
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self.sidebar = ttk.Frame(self.main_frame, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar.pack_propagate(False)  # Prevent sidebar from shrinking
        
        # Sidebar content
        sidebar_label = ttk.Label(self.sidebar, text="Sidebar", font=("Arial", 14, "bold"))
        sidebar_label.pack(pady=10)
        
        # Add some sidebar buttons
        # Checkbox for draw_bboxes
        self.draw_bboxes_var = tk.BooleanVar(value=True)
        draw_bboxes_cb = ttk.Checkbutton(
            self.sidebar, text="Draw Bounding Boxes", variable=self.draw_bboxes_var,
            command=self.on_draw_bboxes_changed
        )
    
        draw_bboxes_cb.pack(fill=tk.X, padx=10, pady=5)

        # Checkbox for delete_japanese
        self.delete_japanese_var = tk.BooleanVar(value=False)
        delete_japanese_cb = ttk.Checkbutton(
            self.sidebar, text="Delete Japanese", variable=self.delete_japanese_var,
            command=self.on_delete_japanese_changed
        )
        delete_japanese_cb.pack(fill=tk.X, padx=10, pady=5)

        # Checkbox for text_outline
        self.text_outline_var = tk.BooleanVar(value=True)
        text_outline_cb = ttk.Checkbutton(
            self.sidebar, text="Text Outline", variable=self.text_outline_var,
            command=self.on_text_outline_changed
        )
        text_outline_cb.pack(fill=tk.X, padx=10, pady=5)

        # Font size control
        font_size_label = ttk.Label(self.sidebar, text="Font Size:")
        font_size_label.pack(padx=10, pady=(15, 0), anchor="w")
        self.font_size_var = tk.IntVar(value=20)
        font_size_spin = ttk.Spinbox(
            self.sidebar, from_=8, to=72, textvariable=self.font_size_var, width=5,
            command=self.on_font_size_changed
        )
        font_size_spin.pack(fill=tk.X, padx=10, pady=5)
        
        # Font dropdown
        font_label = ttk.Label(self.sidebar, text="Font:")
        font_label.pack(padx=10, pady=(15, 0), anchor="w")
        self.font_var = tk.StringVar(value="Arial")
        self.font_dropdown = ttk.Combobox(
            self.sidebar,
            textvariable=self.font_var,
            values=get_available_fonts(),
            state="readonly"
        )
        self.font_dropdown.pack(fill=tk.X, padx=10, pady=5)
        self.font_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_font_changed())

        # Stroke width control
        stroke_width_label = ttk.Label(self.sidebar, text="Stroke Width:")
        stroke_width_label.pack(padx=10, pady=(15, 0), anchor="w")
        self.stroke_width_var = tk.IntVar(value=2)
        stroke_width_spin = ttk.Spinbox(
            self.sidebar, from_=0, to=10, textvariable=self.stroke_width_var, width=5,
            command=self.on_stroke_width_changed
        )
        stroke_width_spin.pack(fill=tk.X, padx=10, pady=5)

        # OCR to Clipboard button
        ocr_btn = ttk.Button(
            self.sidebar,
            text="OCR to Clipboard",
            command=self.ocr_to_clipboard
        )
        ocr_btn.pack(fill=tk.X, padx=10, pady=10)

        # Create main content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Main content
        content_label = ttk.Label(self.content_frame, text="PNG Image Viewer", font=("Arial", 16))
        content_label.pack(pady=10)



        self.translation_index_path = os.path.join(self.workspace_directory, "translation_index.json")

        with open(self.translation_index_path, "r") as f:
            self.png_paths_dict = json.load(f)

        self.png_path_list = list(self.png_paths_dict.keys())
        
        self.selected_png = tk.StringVar(value=self.png_path_list[0] if self.png_path_list else "")
        self.png_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=self.selected_png,
            values=self.png_path_list,
            state="readonly"
        )

        # Add filter entry and dropdown above the PNG dropdown
        self.filter_var = tk.StringVar(value="story")
        self.filter_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=self.filter_var,
            values=list(set(k.split("\\")[0] for k in self.png_path_list)),
            state="readonly",
            width=30
        )
        self.filter_dropdown.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 0))
        self.filter_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_png_dropdown())
        self.filter_dropdown.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 0))
        self.filter_dropdown.insert(0, "")
        self.filter_dropdown.bind("<KeyRelease>", lambda e: self.update_png_dropdown())

        def update_png_dropdown(self):
            filter_text = self.filter_var.get().lower()
            filtered_list = [k for k in self.png_path_list if k.startswith(filter_text)]
            self.png_dropdown["values"] = filtered_list
            # If current selection is not in filtered list, clear selection
            if self.selected_png.get() not in filtered_list:
                self.selected_png.set(filtered_list[0] if filtered_list else "")
        update_png_dropdown(self)
        # Attach the method to the class
        self.update_png_dropdown = update_png_dropdown.__get__(self)

        # Place dropdown at the very top of the content frame
        self.png_dropdown.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))
        self.png_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_png_key_changed())

        # Create frame for images
        self.image_frame = ttk.Frame(self.content_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left image with scrollbars
        self.left_image_frame = ttk.Frame(self.image_frame)
        self.left_image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.left_image_label = ttk.Label(self.left_image_frame, text="Left Image")
        self.left_image_label.pack(pady=5)
        
        # Create canvas with scrollbars for left image
        self.left_canvas_frame = ttk.Frame(self.left_image_frame)
        self.left_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.left_canvas = tk.Canvas(self.left_canvas_frame, background="lightgray")
        self.left_v_scrollbar = ttk.Scrollbar(self.left_canvas_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_h_scrollbar = ttk.Scrollbar(self.left_canvas_frame, orient="horizontal", command=self.left_canvas.xview)
        self.left_canvas.configure(yscrollcommand=self.left_v_scrollbar.set, xscrollcommand=self.left_h_scrollbar.set)
        
        self.left_v_scrollbar.pack(side="right", fill="y")
        self.left_h_scrollbar.pack(side="bottom", fill="x")
        self.left_canvas.pack(side="left", fill="both", expand=True)
        
        # Right image with scrollbars
        self.right_image_frame = ttk.Frame(self.image_frame)
        self.right_image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.right_image_label = ttk.Label(self.right_image_frame, text="Right Image")
        self.right_image_label.pack(pady=5)
        
        # Create canvas with scrollbars for right image
        self.right_canvas_frame = ttk.Frame(self.right_image_frame)
        self.right_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.right_canvas = tk.Canvas(self.right_canvas_frame, background="lightgray")
        self.right_v_scrollbar = ttk.Scrollbar(self.right_canvas_frame, orient="vertical", command=self.right_canvas.yview)
        self.right_h_scrollbar = ttk.Scrollbar(self.right_canvas_frame, orient="horizontal", command=self.right_canvas.xview)
        self.right_canvas.configure(yscrollcommand=self.right_v_scrollbar.set, xscrollcommand=self.right_h_scrollbar.set)
        
        self.right_v_scrollbar.pack(side="right", fill="y")
        self.right_h_scrollbar.pack(side="bottom", fill="x")
        self.right_canvas.pack(side="left", fill="both", expand=True)
        
        # Create control frame for text entry and navigation buttons
        self.control_frame = ttk.Frame(self.content_frame)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Text entry field
        self.entry_label = ttk.Label(self.control_frame, text="Enter text:", font=("Arial", 12))
        self.entry_label.pack(pady=5)
        
        self.text_entry = ttk.Entry(self.control_frame, font=("Arial", 12), width=50)
        self.text_entry.pack(pady=5)
        
        # Navigation buttons frame
        self.nav_frame = ttk.Frame(self.control_frame)
        self.nav_frame.pack(pady=10)

        # Left arrow button
        self.left_arrow_btn = ttk.Button(self.nav_frame, text="◀ Left", command=self.left_arrow_clicked)
        self.left_arrow_btn.pack(side=tk.LEFT, padx=10)

        # Middle button
        self.middle_btn = ttk.Button(self.nav_frame, text="Insert Text", command=self.middle_btn_clicked)
        self.middle_btn.pack(side=tk.LEFT, padx=10)

        # Right arrow button
        self.right_arrow_btn = ttk.Button(self.nav_frame, text="Right ▶", command=self.right_arrow_clicked)
        self.right_arrow_btn.pack(side=tk.RIGHT, padx=10)

        # adjust box height
        adjust_box_height_label = ttk.Label(self.sidebar, text="Adjust Box Height:")
        adjust_box_height_label.pack(padx=10, pady=(15, 0), anchor="w")
        self.adjust_box_height_var = tk.IntVar(value=0)
        adjust_box_height = ttk.Spinbox(
            self.sidebar, from_=0, to=100, textvariable=self.adjust_box_height_var, width=5,
            command=self.on_adjust_box_height_changed
        )
        adjust_box_height.pack(fill=tk.X, padx=10, pady=5)

        #adjust box 'right' position
        adjust_box_right_label = ttk.Label(self.sidebar, text="Adjust Box Right Position:")
        adjust_box_right_label.pack(padx=10, pady=(15, 0), anchor="w")
        self.adjust_box_right_var = tk.IntVar(value=0)
        adjust_box_right = ttk.Spinbox(
            self.sidebar, from_=0, to=512, textvariable=self.adjust_box_right_var, width=5,
            command=self.on_adjust_box_right_changed
        )
        adjust_box_right.pack(fill=tk.X, padx=10, pady=5)

        #adjust box y position
        adjust_box_y_label = ttk.Label(self.sidebar, text="Adjust Box Y Position:")
        adjust_box_y_label.pack(padx=10, pady=(15, 0), anchor="w")
        self.adjust_box_y_var = tk.IntVar(value=0)
        adjust_box_y = ttk.Spinbox(
            self.sidebar, from_=0, to=1024, textvariable=self.adjust_box_y_var, width=5,
            command=self.on_adjust_box_y_changed
        )
        adjust_box_y.pack(fill=tk.X, padx=10, pady=5)

        #adjust box x position
        adjust_box_x_label = ttk.Label(self.sidebar, text="Adjust Box X Position:")
        adjust_box_x_label.pack(padx=10, pady=(15, 0), anchor="w")
        self.adjust_box_x_var = tk.IntVar(value=0)
        adjust_box_x = ttk.Spinbox(
            self.sidebar, from_=0, to=512, textvariable=self.adjust_box_x_var, width=5,
            command=self.on_adjust_box_x_changed
        )
        adjust_box_x.pack(fill=tk.X, padx=10, pady=5)

        # Button to save font preset
        save_font_preset_btn = ttk.Button(
            self.sidebar,
            text="Save Font Preset",
            command=self.save_font_preset
        )
        save_font_preset_btn.pack(fill=tk.X, padx=10, pady=10)

        # Button to load font preset
        load_font_preset_btn = ttk.Button(
            self.sidebar,
            text="Load Font Preset",
            command=self.load_font_preset
        )
        load_font_preset_btn.pack(fill=tk.X, padx=10, pady=10)

        # button to delete and reinitialize write_config.json
        reinitialize_btn = ttk.Button(
            self.sidebar,
            text="Reinitialize this translation",
            command=self.reinitialize_write_config
        )
        reinitialize_btn.pack(fill=tk.X, padx=10, pady=10)

        # Button to build TXDs
        build_txds_btn = ttk.Button(
            self.sidebar,
            text="Build TXDs",
            command=self.build_txds
        )
        build_txds_btn.pack(fill=tk.X, padx=10, pady=10)

        

    def initialize_write_config(self):
        # Initialize the write_config.json file with default values
        write_config_json = {
            "original_png": self.original_png,
            "output_png": self.output_png,
            "draw_bboxes": True,
            "delete_japanese": False,
            "font_size": 20,
            "font_name": "Gadugi-Bold",
            "text_color": "white",
            "text_outline": True,
            "stroke_width": 1,
            "lines": [""] * len(self.bboxes) if self.bboxes else None,
            "bboxes": self.bboxes
        }
        with open(self.translation_index_path, 'r') as f:
            index_data = json.load(f)
        # Only update if the key exists
        if self.selected_png_path in index_data:
            index_data[self.selected_png_path] = write_config_json
            with open(self.translation_index_path, 'w') as f:
                json.dump(index_data, f, indent=4)
        else:
            raise KeyError(f"Key '{self.selected_png_path}' not found in translation_index.json")

    def save_write_config(self):
        """
        Save the current configuration to write_config.json.
        
        Args:
            self.write_config_path: Path to the write_config.json file
        """
        write_config_json = {
            "original_png": self.original_png,
            "output_png": self.output_png,
            "draw_bboxes": self.draw_bboxes,
            "delete_japanese": self.delete_japanese,
            "font_size": self.font_size,
            "font_name": self.font_name,
            "text_color": self.text_color,
            "text_outline": self.text_outline,
            "stroke_width": self.stroke_width,
            "lines": self.lines,
            "bboxes": self.bboxes,
            "timestamp": datetime.now().isoformat()  # Add timestamp for tracking changes
        }
        
        with open(self.translation_index_path, 'r') as f:
            index_data = json.load(f)
        # Only update if the key exists
        if self.selected_png_path in index_data:
            index_data[self.selected_png_path] = write_config_json
            with open(self.translation_index_path, 'w') as f:
                json.dump(index_data, f, indent=4)
        else:
            raise KeyError(f"Key '{self.selected_png_path}' not found in translation_index.json")

    def apply_write_config(self):
        """
        Apply the write config JSON to the image processing functions.
        
        Args:
            write_config_json: Dictionary containing configuration options
        """

        if os.path.exists(self.output_png):
            os.remove(self.output_png)
        shutil.copy(self.original_png, self.output_png)

        if self.delete_japanese:
            # Erase bounding boxes (make transparent)
            erase_bounding_boxes(self.output_png, self.bboxes, self.output_png)

        print(f"Drawing bounding boxes: {self.bboxes[self.selected_bbox] if self.bboxes else 'None'}")
        if (self.draw_bboxes and self.bboxes):
            draw_bounding_boxes(self.output_png, self.bboxes, self.output_png, 
                                selected_bbox=self.selected_bbox, skip=False)  

        # Write text onto the image
        if self.lines:
            for i, bbox in enumerate(self.bboxes):
                x=bbox["x"]
                y=bbox["bottom"]
                height=bbox["height"]
                if self.lines[i] != "":
                    write_onto_png(self.output_png, self.output_png, self.lines[i],
                                font_size=self.font_size, x=x, y=y, height=height, color=self.text_color, 
                                font_path=os.path.join(self.workspace_directory, "gadugi-bold.ttf"), stroke_width=self.stroke_width, text_outline=self.text_outline)
        convert_png_to_P(self.output_png) 
        self.save_write_config()

    def read_write_config(self):
        """
        Read the write_config.json file and return its contents.
        
        Args:
            self.write_config_path: Path to the write_config.json file
        Returns:
            Dictionary containing the configuration options
        """
        with open(self.translation_index_path, 'r') as f:
            index_data = json.load(f)

        if self.selected_png_path in index_data:
            write_config_json = index_data[self.selected_png_path]
        else:
            raise KeyError(f"Key '{self.selected_png_path}' not found in translation_index.json")

        self.original_png = write_config_json['original_png']
        self.output_png = write_config_json['output_png']
        self.draw_bboxes = write_config_json['draw_bboxes']
        self.draw_bboxes_var.set(self.draw_bboxes)
        self.delete_japanese = write_config_json['delete_japanese']
        self.delete_japanese_var.set(self.delete_japanese)
        self.font_size = write_config_json['font_size']
        self.font_size_var.set(self.font_size)
        self.font_name = write_config_json['font_name']
        self.font_var.set(self.font_name)
        self.text_color = write_config_json['text_color']
        self.text_outline = write_config_json['text_outline']
        self.lines = write_config_json['lines']
        self.bboxes = write_config_json['bboxes']
        self.adjust_box_height_var.set(self.bboxes[self.selected_bbox]["height"])
        self.adjust_box_x_var.set(self.bboxes[self.selected_bbox]["x"])
        self.adjust_box_right_var.set(self.bboxes[self.selected_bbox]["right"])
        self.adjust_box_y_var.set(self.bboxes[self.selected_bbox]["y"])
        self.stroke_width = write_config_json['stroke_width']
        self.stroke_width_var.set(self.stroke_width)

        return write_config_json

    def load_images(self):
        
        # Initialize selected bounding box index
        self.selected_bbox = 0 

        # Replace these paths with your actual PNG file paths
        self.original_png = os.path.join(self.workspace_directory, "root_unpacked_txd", self.selected_png_path)
        # Ensure all parent directories for output_png exist
        self.output_png = os.path.join(self.workspace_directory, "root_translated_pngs", self.selected_png_path)
        os.makedirs(os.path.dirname(self.output_png), exist_ok=True)
        

        self.bboxes = detect_bounding_boxes(self.original_png)
        with open(self.translation_index_path, 'r') as f:
            index_data = json.load(f)

        if self.selected_png_path not in index_data:
            raise KeyError(f"Key '{self.selected_png_path}' not found in translation_index.json")
        elif index_data[self.selected_png_path] is None:
            self.initialize_write_config()

        self.read_write_config()
        self.apply_write_config()

        if self.lines and 0 <= self.selected_bbox < len(self.lines):
            self.text_entry.insert(0, self.lines[self.selected_bbox])

        with open(self.original_png, 'rb') as f:
            left_img = Image.open(f)
            self.left_photo = ImageTk.PhotoImage(left_img)

        # Clear canvas and add image
        self.left_canvas.delete("all")
        self.left_canvas.create_image(0, 0, anchor="nw", image=self.left_photo)
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        
        # Load right image at original size
        with open(self.output_png, 'rb') as f:
            right_img = Image.open(f)
            self.right_photo = ImageTk.PhotoImage(right_img)

        # Clear canvas and add image
        self.right_canvas.delete("all")
        self.right_canvas.create_image(0, 0, anchor="nw", image=self.right_photo)
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
            

    def refresh_output_image(self):
        """
        Update the right image based on the current configuration.
        """
        self.save_write_config()
        # Apply the write config to the output image
        self.apply_write_config()

        # Load right image at original size
        with open(self.output_png, 'rb') as f:
            right_img = Image.open(f)
            self.right_photo = ImageTk.PhotoImage(right_img)

        # Clear canvas and add image
        self.right_canvas.delete("all")
        self.right_canvas.create_image(0, 0, anchor="nw", image=self.right_photo)
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))

    def on_draw_bboxes_changed(self):
        """
        Callback for when the draw_bboxes checkbox is changed.
        """
        self.draw_bboxes = self.draw_bboxes_var.get()
        print(f"Draw Bounding Boxes: {self.draw_bboxes}")
        self.refresh_output_image()

    def on_delete_japanese_changed(self):
        """
        Callback for when the delete_japanese checkbox is changed.
        """
        self.delete_japanese = self.delete_japanese_var.get()
        print(f"Delete Japanese: {self.delete_japanese}")
        self.refresh_output_image()

    def on_text_outline_changed(self):
        """
        Callback for when the text_outline checkbox is changed.
        """
        self.text_outline = self.text_outline_var.get()
        print(f"Text Outline: {self.text_outline}")
        self.refresh_output_image()

    def on_font_size_changed(self):
        """
        Callback for when the font size is changed.
        """
        self.font_size = self.font_size_var.get()
        print(f"Font Size: {self.font_size}")
        self.refresh_output_image()

    def on_stroke_width_changed(self):
        """
        Callback for when the stroke width is changed.
        """
        self.stroke_width = self.stroke_width_var.get()
        print(f"Stroke Width: {self.stroke_width}")
        self.refresh_output_image()

    def left_arrow_clicked(self):
        current_text = self.text_entry.get()
        print(f"Left arrow clicked. Current text: {current_text}")
        self.selected_bbox -= 1 if self.selected_bbox > 0 else 0
        self.adjust_box_height_var.set(self.bboxes[self.selected_bbox]["height"])
        self.adjust_box_right_var.set(self.bboxes[self.selected_bbox]["right"])
        self.adjust_box_y_var.set(self.bboxes[self.selected_bbox]["y"])
        self.adjust_box_x_var.set(self.bboxes[self.selected_bbox]["x"])
        self.refresh_output_image()
        self.text_entry.delete(0, tk.END)
        if self.lines and 0 <= self.selected_bbox < len(self.lines):
            self.text_entry.insert(0, self.lines[self.selected_bbox])

    def middle_btn_clicked(self):
        current_text = self.text_entry.get()
        print(f"Middle button clicked. Current text: {current_text}")
        if self.selected_bbox < len(self.bboxes):
            self.lines[self.selected_bbox] = current_text
            self.refresh_output_image()
        else:
            print("No bounding box selected or index out of range.")

    def ocr_to_clipboard(self):
        if not self.bboxes or len(self.bboxes) == 0:
            print("No bounding boxes found.")
            return

        bbox = self.bboxes[2]
        # Crop the image to the bbox and ensure RGBA
        with Image.open(self.original_png) as img:
            img = img.convert("RGBA")
            nump_img = np.array(img)
            # If image has alpha, set transparent pixels to black
            if nump_img.shape[-1] == 4:
                alpha = nump_img[..., 3]
                mask = (alpha == 0)
                nump_img[mask] = [0, 0, 0, 255]
                img = Image.fromarray(nump_img)
            img.save("temp_img.png")
        reader = easyocr.Reader(['ja'])
        result = reader.readtext("temp_img.png")
        # Concatenate all detected text
        text = "".join([item[1] for item in result])
        text = "\n".join([t for t in text.split("。") if t]).strip()

        pyperclip.copy(text)
        print(f"OCR copied to clipboard: {text}")

    def on_font_changed(self):
        self.font_name = self.font_var.get()
        print(f"Font changed: {self.font_name}")
        self.refresh_output_image()

    def on_png_key_changed(self):
        self.selected_png_path = self.selected_png.get()
        print(f"PNG key changed: {self.selected_png_path}")
        self.load_images()

    def right_arrow_clicked(self):
        current_text = self.text_entry.get()
        print(f"Right arrow clicked. Current text: {current_text}")
        self.selected_bbox += 1 if self.selected_bbox < len(self.bboxes) - 1 else 0
        self.adjust_box_height_var.set(self.bboxes[self.selected_bbox]["height"])
        self.adjust_box_right_var.set(self.bboxes[self.selected_bbox]["right"])
        self.adjust_box_y_var.set(self.bboxes[self.selected_bbox]["y"])
        self.adjust_box_x_var.set(self.bboxes[self.selected_bbox]["x"])
        self.refresh_output_image()
        self.text_entry.delete(0, tk.END)
        if self.lines and 0 <= self.selected_bbox < len(self.lines):
            self.text_entry.insert(0, self.lines[self.selected_bbox])

    def on_adjust_box_height_changed(self):
        new_height = self.adjust_box_height_var.get()
        print(f"Adjust box height changed: {new_height}")
        if self.selected_bbox < len(self.bboxes):
            self.bboxes[self.selected_bbox]["height"] = new_height
            self.bboxes[self.selected_bbox]["bottom"] = self.bboxes[self.selected_bbox]["y"] + new_height
            self.refresh_output_image()

    def on_adjust_box_right_changed(self):
        new_right = self.adjust_box_right_var.get()
        print(f"Adjust box right position changed: {new_right}")
        if self.selected_bbox < len(self.bboxes):
            self.bboxes[self.selected_bbox]["right"] = new_right
            self.refresh_output_image()

    def on_adjust_box_y_changed(self):
        new_y = self.adjust_box_y_var.get()
        print(f"Adjust box Y position changed: {new_y}")
        if self.selected_bbox < len(self.bboxes):
            self.bboxes[self.selected_bbox]["y"] = new_y
            self.bboxes[self.selected_bbox]["bottom"] = new_y + self.bboxes[self.selected_bbox]["height"]
            self.refresh_output_image()

    
    def on_adjust_box_x_changed(self):
        new_x = self.adjust_box_x_var.get()
        print(f"Adjust box X position changed: {new_x}")
        if self.selected_bbox < len(self.bboxes):
            self.bboxes[self.selected_bbox]["x"] = new_x
            self.bboxes[self.selected_bbox]["right"] = new_x + self.bboxes[self.selected_bbox]["width"]
            self.refresh_output_image()

    # Add method to save font preset
    def save_font_preset(self):

        preset = {
            "font_name": self.font_var.get(),
            "font_size": self.font_size_var.get(),
            "stroke_width": self.stroke_width_var.get(),
            "text_outline": self.text_outline_var.get()
        }
        # Prompt user for save location
        preset_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir=os.path.join(self.workspace_directory, "font_presets"),
            title="Save Font Preset As"
        )
        if not preset_path:
            print("Save cancelled.")
            return
        try:
            with open(preset_path, "w") as f:
                json.dump(preset, f, indent=4)
            print(f"Font preset saved to {preset_path}")
            messagebox.showinfo("Success", f"Font preset saved to:\n{preset_path}")
        except Exception as e:
            print(f"Error saving font preset: {e}")
            messagebox.showerror("Error", f"Failed to save font preset:\n{e}")

    # Add method to load font preset
    def load_font_preset(self):
        # Prompt user for file to load
        preset_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir=os.path.join(self.workspace_directory, "font_presets"),
            title="Load Font Preset"
        )
        if not preset_path:
            print("Load cancelled.")
            return
        try:
            with open(preset_path, "r") as f:
                preset = json.load(f)
            self.font_name = preset["font_name"]
            self.font_size = preset["font_size"]
            self.stroke_width = preset["stroke_width"]
            self.text_outline = preset["text_outline"]

            self.font_var.set(preset["font_name"])
            self.font_size_var.set(preset["font_size"])
            self.stroke_width_var.set(preset["stroke_width"])
            self.text_outline_var.set(preset["text_outline"])
            print(f"Font preset loaded from {preset_path}")
            messagebox.showinfo("Success", f"Font preset loaded from:\n{preset_path}")
            self.refresh_output_image()
        except Exception as e:
            print(f"Error loading font preset: {e}")
            messagebox.showerror("Error", f"Failed to load font preset:\n{e}")

    def reinitialize_write_config(self):
        answer = messagebox.askyesno(
            "Confirm Reinitialize",
            "Are you sure you want to reinitialize this index entry? Any changes you have made to this png will be lost."
        )
        if not answer:
            print("Reinitialize cancelled by user.")
            return
        try:
            self.initialize_write_config()
            self.read_write_config()
            self.refresh_output_image()
            messagebox.showinfo("Success", "write_config.json reinitialized successfully.")
        except Exception as e:
            print(f"Error reinitializing write_config.json: {e}")
            messagebox.showerror("Error", f"Failed to reinitialize write_config.json:\n{e}")
    
    def build_txds(self):
        answer = messagebox.askyesno(
            "Confirm Build TXDs",
            "Are you sure you want to build TXDs? This may take a while"
        )
        if not answer:
            print("Build TXDs cancelled by user.")
            return
        repacked_txds_dir = os.path.join(self.workspace_directory, "root_repacked_txds")
        os.makedirs(repacked_txds_dir, exist_ok=True)

        mass_build_txd(
            os.path.join(self.workspace_directory, "root_translated_pngs"),
            repacked_txds_dir,
            click_build_button=True
        )

        # Check if magic.txd process is running
        def is_magic_txd_running():
            return any(
                "magictxd.exe" in (p.name() or "").lower() or "magic_txd" in (p.name() or "").lower()
                for p in psutil.process_iter(['name'])
            )

        while is_magic_txd_running():
            messagebox.showwarning(
                "Warning",
                "Batch build job may still be running.\nWait for it to finish.\nWhen done, close Magic TXD and click OK"
            )
        
        messagebox.showinfo("Success", "TXDs built successfully. You may now pack .fpks with the new TXDs.")



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()