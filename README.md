The PDF OCR Tool is a Python-based GUI application designed to convert PDF files into plain text. It extracts text from PDF files and employs Optical Character Recognition (OCR) when necessary to process images within the PDF. The tool supports processing individual PDF files or entire folders.

Table of Contents
Features
Installation
Usage
Support and Contribution
License
Features
Graphical User Interface: Easily select and process PDF files or folders.
Text Extraction: Directly extract text from PDF files when available.
OCR Processing: Utilize OCR to convert images within PDFs into text.
Multi-threading: Speed up processing using concurrent threads.
Progress Bar: Monitor the progress of the PDF processing.
Logging: Keep track of the processing with detailed log files.
Configuration: Customize the output directory using a configuration file.
Installation
Dependencies
The following libraries are required:

fitz (PyMuPDF)
pytesseract
PIL (Pillow)
numpy
tqdm
tkinter
You can install these dependencies using pip:

bash
Copy code
pip install PyMuPDF pytesseract Pillow numpy tqdm
Configuration
Create a config.ini file in the project directory and set up the output directory:

ini
Copy code
[DEFAULT]
OutputDirectory = path/to/output/directory
Replace path/to/output/directory with the actual path where you want to save the processed text files.

Usage
Simply run the script:

bash
Copy code
python path/to/pdf_ocr_tool.py
The GUI will appear, allowing you to select PDF files or folders for processing.

Support and Contribution
If you encounter any issues or have suggestions for improvement, please feel free to open an issue or submit a pull request.



