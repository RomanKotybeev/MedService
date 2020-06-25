import os
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_file(file):
    path = os.path.join(BASE_DIR, str(file))
    text = None
    with open(path) as f:
        text = f.read()
    return text


def txt_or_img(*uploaded_files):
    med_text = ''
    for file in uploaded_files:
        if file.name.endswith('.txt'):
            for chunk in file.chunks(chunk_size=2):
                med_text += chunk.decode(encoding='utf-8')
        else:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            med_text += pytesseract.image_to_string(Image.open(file), lang='rus')
    return med_text


def read_comments():
    with open(os.path.join(os.getcwd(), 'list_diseases\\comments'), encoding='UTF-8') as f:
        comments = f.read()
    return comments

