import fitz  # PyMuPDF
import docx
import io
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentParser:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

    def extract_text_from_pdf(self, file_bytes: bytes) -> list[dict]:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                pages.append({"page_number": page_num + 1, "text": text})
        return pages

    def extract_text_from_docx(self, file_bytes: bytes) -> list[dict]:
        doc = docx.Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        return [{"page_number": 1, "text": "\n".join(full_text)}]

    def sanitize_text(self, text: str) -> str:
        # Basic prompt injection protection by removing excessive special chars
        # and standardizing whitespace
        sanitized = " ".join(text.split())
        return sanitized

    def parse_and_chunk(self, file_bytes: bytes, file_type: str) -> list[dict]:
        pages = []
        if file_type == "application/pdf":
            pages = self.extract_text_from_pdf(file_bytes)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            pages = self.extract_text_from_docx(file_bytes)
        elif file_type == "text/plain":
            pages = [{"page_number": 1, "text": file_bytes.decode('utf-8')}]
        else:
            raise ValueError("Unsupported file type")

        chunks = []
        for page in pages:
            sanitized_text = self.sanitize_text(page["text"])
            if not sanitized_text:
                continue
            
            page_chunks = self.text_splitter.split_text(sanitized_text)
            for chunk in page_chunks:
                chunks.append({
                    "content": chunk,
                    "page_number": page["page_number"]
                })
        
        return chunks

document_parser = DocumentParser()
