import os
import threading
from time import sleep
import tkinter as tk
from tkinter import filedialog, ttk
import logging


class PDFToolGUI:
    def __init__(self, root, processor):
        self.processor = processor
        self.root = root
        self.init_gui()

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        self.processor.output_directory = folder_path
        self.output_folder_path_label.config(text="Output Folder: " + folder_path)
        self.check_start_button_state()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_label.config(text="Folder: " + folder_path)
        self.check_start_button_state()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.file_path_label.config(text="File: " + file_path)
        self.check_start_button_state()

    def process_files(self, path, is_folder):
        # Check if the output directory has been selected

        # Proceed with processing if the output directory is set
        if self.processor.output_directory:
            self.status_label.config(text="Processing...")
            threading.Thread(target=self.background_processing, args=(path, is_folder)).start()
        else:
            self.status_label.config(text="Output directory not selected. Processing aborted.")

    # ...

    def background_processing(self, path, is_folder):  # Indentation fixed to include method within the class
        logging.info(f"Processing files from {path}")
        if is_folder:
            pdf_files = [filename for filename in os.listdir(path) if filename.endswith(".pdf")]
        else:
            pdf_files = [os.path.basename(path)]
            path = os.path.dirname(path)

        self.progress_bar["maximum"] = len(pdf_files)
        for filename in pdf_files:
            self.processor.process_pdf(filename, path)
            self.root.after(0, self.progress_bar.step)  # Schedule the step update in the main thread
            self.root.update_idletasks()
            sleep(0.1)
        self.status_label.config(text="Processing complete.")

    # ...


    def init_gui(self):
        logging.info("Initializing GUI")

        # Create main frame with padding
        frame = ttk.Frame(self.root, padding="10 10 10 10")
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid expansion
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        for i in range(8):
            frame.rowconfigure(i, weight=1)

        # Buttons for selecting folders and files
        folder_button = ttk.Button(frame, text="Select Folder", command=self.select_folder)
        folder_button.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        file_button = ttk.Button(frame, text="Select PDF File", command=self.select_file)
        file_button.grid(row=1, column=0, pady=5, padx=5, sticky="ew")

        output_folder_button = ttk.Button(frame, text="Select Output Folder", command=self.select_output_folder)
        output_folder_button.grid(row=2, column=0, pady=5, padx=5, sticky="ew")
        
        self.start_button = ttk.Button(self.root, text="Start Processing", command=self.start_processing, state=tk.DISABLED)
        self.start_button.grid(row=8, column=0, pady=5, padx=5, sticky="ew")
        

        # Labels for displaying selected paths
        self.folder_path_label = ttk.Label(frame, text="Folder: Not selected", wraplength=300)
        self.folder_path_label.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        self.file_path_label = ttk.Label(frame, text="PDF File: Not selected", wraplength=300)
        self.file_path_label.grid(row=4, column=0, pady=5, padx=5, sticky="w")

        self.output_folder_path_label = ttk.Label(frame, text="Output Folder: Not selected", wraplength=300)
        self.output_folder_path_label.grid(row=5, column=0, pady=5, padx=5, sticky="w")

        # Status label
        self.status_label = ttk.Label(frame, text="Status: Waiting", wraplength=300)
        self.status_label.grid(row=6, column=0, pady=5, padx=5, sticky="w")

        # Progress bar for tracking progress
        self.progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=7, column=0, pady=5, padx=5, sticky="ew")

    def check_start_button_state(self):
        if self.folder_path_label.cget("text") != "Folder: Not selected" and \
           self.output_folder_path_label.cget("text") != "Output Folder: Not selected":
            self.start_button.config(state=tk.NORMAL)
    
    def start_processing(self):  # Indentation fixed to include method within the class
        # Determine whether a folder or file has been selected
        folder_selected = self.folder_path_label.cget("text") != "Folder: Not selected"
        file_selected = self.file_path_label.cget("text") != "PDF File: Not selected"

        # Path to the selected folder or file
        path = None
        is_folder = False

        if folder_selected:
            path = self.folder_path_label.cget("text")[len("Folder: "):]
            is_folder = True
        elif file_selected:
            path = self.file_path_label.cget("text")[len("PDF File: "):]

        # Start processing if a valid folder or file has been selected
        if path:
            self.process_files(path, is_folder)
        else:
            self.status_label.config(text="No folder or file selected. Processing aborted.")