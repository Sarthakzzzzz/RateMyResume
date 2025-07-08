# d:\RateMyResume\App\models\recieve.py

from django import forms
from App.models.resume import Resume
import fitz  # PyMuPDF
import docx


def extract_text_from_pdf(file):
    file.seek(0)
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    return text


def extract_text_from_docx(file):
    file.seek(0)
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['uploaded_file']
