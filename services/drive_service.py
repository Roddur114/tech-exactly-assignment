import os
import io
import platform
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from docx import Document
import PyPDF2
from constant.constant import ProjectConstant 

if platform.system() == 'Windows':
    import win32com.client

def list_files(creds):
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q="mimeType='application/pdf' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mimeType='application/msword'",
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

def extract_txt_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_docx_content(file_path):
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_pdf_content(file_path):
    content = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            content += page.extract_text() or ''
    return content

def extract_doc_content(file_path):
    if platform.system() == 'Windows':
        try:
            word = win32com.client.Dispatch("Word.Application")
            doc = word.Documents.Open(file_path)
            text = doc.Content.Text
            doc.Close()
            word.Quit()
            return text
        except Exception as e:
            return f"[Error extracting .doc file: {e}]"
    else:
        return "[.doc extraction is only supported on Windows with pywin32]"

def extract_content(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return extract_txt_content(file_path)
    elif ext == '.docx':
        return extract_docx_content(file_path)
    elif ext == '.pdf':
        return extract_pdf_content(file_path)
    elif ext == '.doc':
        return extract_doc_content(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def download_file_content(creds, file_id):
    service = build('drive', 'v3', credentials=creds)
    file = service.files().get(fileId=file_id, fields="name").execute()
    name = file['name']
    file_path = os.path.join(ProjectConstant.DOWNLOAD_FOLDER, name)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()

    try:
        content = extract_content(file_path)
    except Exception as e:
        content = f"[Error extracting {name}]: {e}"

    return name, content
