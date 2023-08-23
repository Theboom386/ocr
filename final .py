import fitz
import pytesseract
from PIL import Image
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, ttk
import configparser
import logging

# Configuration setup
config = configparser.ConfigParser()
config.read('config.ini')
output_directory = config['DEFAULT']['OutputDirectory']

# Logging setup
logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(message)s')


class PDFProcessor:
    def __init__(self, output_directory):
        self.output_directory = output_directory

    def process_page(self, page_num, doc, text_file):
        try:
            page = doc.load_page(page_num)
            text = page.get_text()
            if not text:  # If no text, use OCR
                pix = page.get_pixmap()
                samples = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
                img = Image.fromarray(samples)
                # Simple resizing as an OCR optimization step
                img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)
                text = pytesseract.image_to_string(img)
            text_file.write(text)
        except Exception as e:
            logging.error(f"Error processing page {page_num}: {e}")

    def process_pdf(self, filename, pdf_folder_path):
        pdf_path = os.path.join(pdf_folder_path, filename)
        original_filename = os.path.splitext(filename)[0]
        output_path = os.path.join(self.output_directory, original_filename + '.txt')

        if os.path.exists(pdf_path):
            try:
                doc = fitz.open(pdf_path)
                with open(output_path, 'w', encoding='utf-8') as text_file:
                    with ThreadPoolExecutor() as executor:
                        list(tqdm(executor.map(lambda page_num: self.process_page(page_num, doc, text_file),
                                              range(len(doc))), total=len(doc), desc=f"Processing {filename}", leave=False))
            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}")

class PDFToolGUI:
    def __init__(self, root, processor):
        self.processor = processor
        self.root = root
        self.init_gui()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        folder_path_label.config(text="Folder: " + folder_path)
        self.process_files(folder_path, is_folder=True)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        file_path_label.config(text="File: " + file_path)
        self.process_files(file_path, is_folder=False)

    def process_files(self, path, is_folder):
        status_label.config(text="Processing...")
        logging.info(f"Processing files from {path}")
        if is_folder:
            pdf_files = [filename for filename in os.listdir(path) if filename.endswith(".pdf")]
        else:
            pdf_files = [os.path.basename(path)]
            path = os.path.dirname(path)

        progress_bar["maximum"] = len(pdf_files)
        for filename in pdf_files:
            self.processor.process_pdf(filename, path)
            progress_bar.step()
        status_label.config(text="Processing complete.")

    def init_gui(self):
        logging.info("Initializing GUI")
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        folder_button = ttk.Button(frame, text="Select Folder", command=self.select_folder)
        folder_button.grid(row=0, column=0, pady=5)

        file_button = ttk.Button(frame, text="Select PDF File", command=self.select_file)
        file_button.grid(row=1, column=0, pady=5)

        global folder_path_label
        folder_path_label = ttk.Label(frame, text="")
        folder_path_label.grid(row=2, column=0, pady=5, sticky=tk.W)

        global file_path_label
        file_path_label = ttk.Label(frame, text="")
        file_path_label.grid(row=3, column=0, pady=5, sticky=tk.W)

        global status_label
        status_label = ttk.Label(frame, text="")
        status_label.grid(row=4, column=0, pady=5, sticky=tk.W)

        global progress_bar
        progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
        progress_bar.grid(row=5, column=0, pady=5)

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

root = tk.Tk()
root.title("PDF OCR Tool")
root.geometry("400x200")

pdf_processor = PDFProcessor(output_directory)
pdf_tool_gui = PDFToolGUI(root, pdf_processor)

root.mainloop()

logging.info('Application exited')

