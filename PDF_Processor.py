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