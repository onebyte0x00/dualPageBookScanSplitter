import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2  # Import OpenCV
import os
import numpy as np

class DualPageSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Page Splitter")
        self.root.geometry("600x450")
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.split_x = tk.IntVar(value=0)
        self.crop_enabled = tk.BooleanVar(value=False)
        self.crop_top = tk.IntVar(value=0)
        self.crop_bottom = tk.IntVar(value=0)
        self.crop_left = tk.IntVar(value=0)
        self.crop_right = tk.IntVar(value=0)
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Input Folder
        ttk.Label(self.root, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.input_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output Folder
        ttk.Label(self.root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.output_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Split X Position
        ttk.Label(self.root, text="Split X Position:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ttk.Scale(self.root, from_=0, to=3000, variable=self.split_x, 
                 orient="horizontal", length=400, command=self.update_split_value).grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        self.split_value_label = ttk.Label(self.root, text="0 px")
        self.split_value_label.grid(row=3, column=1, sticky="w", padx=10)
        
        # Crop Options
        crop_frame = ttk.LabelFrame(self.root, text="Crop Options")
        crop_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="we")
        
        ttk.Checkbutton(crop_frame, text="Enable Cropping", variable=self.crop_enabled).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Label(crop_frame, text="Top:").grid(row=1, column=0, padx=5, pady=2)
        ttk.Entry(crop_frame, textvariable=self.crop_top, width=5).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(crop_frame, text="Bottom:").grid(row=1, column=2, padx=5, pady=2)
        ttk.Entry(crop_frame, textvariable=self.crop_bottom, width=5).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(crop_frame, text="Left:").grid(row=2, column=0, padx=5, pady=2)
        ttk.Entry(crop_frame, textvariable=self.crop_left, width=5).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(crop_frame, text="Right:").grid(row=2, column=2, padx=5, pady=2)
        ttk.Entry(crop_frame, textvariable=self.crop_right, width=5).grid(row=2, column=3, padx=5, pady=2)
        
        # Process Button
        ttk.Button(self.root, text="Process Images", command=self.process_images).grid(row=5, column=1, pady=20)
        
        # Status Bar
        self.status = ttk.Label(self.root, text="Ready", relief="sunken", anchor="w")
        self.status.grid(row=6, column=0, columnspan=3, sticky="we", padx=10, pady=10)
    
    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)
    
    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
    
    def update_split_value(self, event=None):
        self.split_value_label.config(text=f"{self.split_x.get()} px")
    
    def process_images(self):
        input_path = self.input_folder.get()
        output_path = self.output_folder.get()
        split_x = self.split_x.get()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select input and output folders")
            return
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        crop_enabled = self.crop_enabled.get()
        crop_values = {
            'top': self.crop_top.get(),
            'bottom': self.crop_bottom.get(),
            'left': self.crop_left.get(),
            'right': self.crop_right.get()
        }
        
        valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
        image_files = [f for f in os.listdir(input_path) 
                      if f.lower().endswith(valid_extensions)]
        
        if not image_files:
            messagebox.showinfo("Info", "No valid images found in the input folder")
            return
        
        self.status.config(text="Processing...")
        self.root.update()
        
        for i, filename in enumerate(image_files):
            try:
                img_path = os.path.join(input_path, filename)
                image = cv2.imread(img_path)
                
                if image is None:
                    continue
                
                # Apply cropping if enabled
                if crop_enabled:
                    h, w = image.shape[:2]
                    top = min(crop_values['top'], h-1)
                    bottom = max(1, h - crop_values['bottom'])
                    left = min(crop_values['left'], w-1)
                    right = max(1, w - crop_values['right'])
                    
                    if top < bottom and left < right:
                        image = image[top:bottom, left:right]
                    else:
                        messagebox.showwarning("Invalid Crop", f"Invalid crop values for {filename}. Skipping crop.")
                
                # Split the image
                h, w = image.shape[:2]
                if split_x < w:
                    left_page = image[:, :split_x]
                    right_page = image[:, split_x:]
                else:
                    left_page = image
                    right_page = None
                
                # Save pages
                base_name = os.path.splitext(filename)[0]
                cv2.imwrite(os.path.join(output_path, f"{base_name}_left.jpg"), left_page)
                if right_page is not None:
                    cv2.imwrite(os.path.join(output_path, f"{base_name}_right.jpg"), right_page)
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
        
        self.status.config(text=f"Processed {len(image_files)} images")
        messagebox.showinfo("Complete", "Processing finished successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = DualPageSplitterApp(root)
    root.mainloop()
