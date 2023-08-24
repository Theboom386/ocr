from Logging_Setup import setup_logging
from PDF_Processor import PDFProcessor
from PDFToolGUI import PDFToolGUI

import logging
import threading
from time import sleep
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
