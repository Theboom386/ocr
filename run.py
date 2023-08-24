import logging

def setup_logging():
    logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(message)s')


import fitz
import pytesseract
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from PIL import Image, ImageFilter, ImageEnhance


class PDFProcessor:
    def __init__(self):
        self._output_directory = None

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value):
        self._output_directory = value

    def process_page(self, page_num, doc, text_file):
        try:
            page = doc.load_page(page_num)
            text = page.get_text()
            if not text:  # If no text, use OCR
                pix = page.get_pixmap()
                samples = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
                img = Image.fromarray(samples)
                img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)
                img = img.filter(ImageFilter.MedianFilter(size=3))  # Noise reduction
                img = ImageEnhance.Contrast(img).enhance(1.5)  # Increasing contrast
                text = pytesseract.image_to_string(img)
            text_file.write(text)
        except Exception as e:
            logging.error(f"Error processing page {page_num}: {e}")

    def process_pdf(self, filename, pdf_folder_path):
        pdf_path = os.path.join(pdf_folder_path, filename)
        original_filename = os.path.splitext(filename)[0]
        output_path = os.path.join(self._output_directory, original_filename + '.txt')

        if os.path.exists(pdf_path):
            try:
                doc = fitz.open(pdf_path)
                with open(output_path, 'w', encoding='utf-8') as text_file:
                    with ThreadPoolExecutor(max_workers=4) as executor:
                        futures = [executor.submit(self.process_page, page_num, doc, text_file) for page_num in range(len(doc))]
                        for future in tqdm(as_completed(futures), total=len(doc), desc=f"Processing {filename}", leave=False):
                            pass
            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}")

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

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_label.config(text="Folder: " + folder_path)
        self.process_files(folder_path, is_folder=True)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.file_path_label.config(text="File: " + file_path)
        self.process_files(file_path, is_folder=False)

    def process_files(self, path, is_folder):
        # Check if the output directory has been selected

        # Proceed with processing if the output directory is set
        if self.processor.output_directory:
            self.status_label.config(text="Processing...")
            threading.Thread(target=self.background_processing, args=(path, is_folder)).start()
        else:
            self.status_label.config(text="Output directory not selected. Processing aborted.")

    def background_processing(self, path, is_folder):
        logging.info(f"Processing files from {path}")
        if is_folder:
            pdf_files = [filename for filename in os.listdir(path) if filename.endswith(".pdf")]
        else:
            pdf_files = [os.path.basename(path)]
            path = os.path.dirname(path)

        self.progress_bar["maximum"] = len(pdf_files)
        for filename in pdf_files:
            self.processor.process_pdf(filename, path)
            self.progress_bar.step()
            self.root.update_idletasks()
            sleep(0.1)
        self.status_label.config(text="Processing complete.")

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


from Logging_Setup import setup_logging
from PDF_Processor import PDFProcessor
from PDFToolGUI import PDFToolGUI


import tkinter as tk
from tqdm import tqdm

# The rest of your imports if there are any...

def main():
    root = tk.Tk()
    root.title("PDF OCR Tool")
    root.geometry("400x200")

    pdf_processor = PDFProcessor()
    pdf_tool_gui = PDFToolGUI(root, pdf_processor)

    root.mainloop()

    logging.info('Application exited')

if __name__ == "__main__":
    setup_logging()  # Make sure to include the logging setup
    main()
