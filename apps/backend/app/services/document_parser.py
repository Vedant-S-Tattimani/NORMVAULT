"""
Document parsing abstractions and concrete implementations.
"""
import abc
import hashlib
import re
from typing import List, Optional
from pydantic import BaseModel

class NormalizedBlock(BaseModel):
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    block_id: Optional[str] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    text: str

class NormalizedDocument(BaseModel):
    blocks: List[NormalizedBlock]
    full_text: str
    page_count: Optional[int] = 1

class DocumentParserProtocol(abc.ABC):
    @abc.abstractmethod
    def parse(self, file_path: str, mime_type: str) -> NormalizedDocument:
        pass

class PdfParser(DocumentParserProtocol):
    """
    Parser for PDF documents. Uses PyMuPDF (fitz) for text extraction.
    Extracts block-level spans with page numbers, coordinates, and offsets.
    Throws OCR_REQUIRED ValueError if no text is found in pages.
    """
    def parse(self, file_path: str, mime_type: str) -> NormalizedDocument:
        import fitz  # PyMuPDF
        
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Corrupted or invalid PDF: {str(e)}")

        num_pages = len(doc)
        if num_pages == 0:
            doc.close()
            raise ValueError("Empty PDF document.")

        blocks: List[NormalizedBlock] = []
        full_text_buffer = []
        current_offset = 0
        current_heading: Optional[str] = None
        has_any_text = False

        for page_idx in range(num_pages):
            page_num = page_idx + 1
            page = doc[page_idx]
            # PyMuPDF get_text("blocks") returns list of:
            # (x0, y0, x1, y1, text, block_no, block_type)
            page_blocks = page.get_text("blocks")
            
            for b_idx, b in enumerate(page_blocks):
                # block_type 0 is text, 1 is image
                if len(b) >= 7 and b[6] != 0:
                    continue
                block_text = b[4].strip()
                if not block_text:
                    continue

                has_any_text = True
                
                # Heading heuristic: Short line ending without period or starting with section numbering
                if len(block_text) < 80 and ("\n" not in block_text) and not block_text.endswith("."):
                    current_heading = block_text

                block_id = f"p{page_num}_b{b_idx + 1}"
                
                # Add spacing separator if buffer not empty
                if full_text_buffer:
                    full_text_buffer.append("\n\n")
                    current_offset += 2

                start_offset = current_offset
                full_text_buffer.append(block_text)
                current_offset += len(block_text)
                end_offset = current_offset

                blocks.append(
                    NormalizedBlock(
                        page_number=page_num,
                        section_heading=current_heading,
                        block_id=block_id,
                        start_offset=start_offset,
                        end_offset=end_offset,
                        text=block_text
                    )
                )

        doc.close()
        full_text = "".join(full_text_buffer)

        # Scanned PDF Detection
        if num_pages > 0 and (not has_any_text or not full_text.strip()):
            raise ValueError("OCR_REQUIRED")

        return NormalizedDocument(
            blocks=blocks,
            full_text=full_text,
            page_count=num_pages
        )

class PlainTextParser(DocumentParserProtocol):
    def parse(self, file_path: str, mime_type: str) -> NormalizedDocument:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if not content.strip():
            raise ValueError("Empty file content.")

        return parse_raw_text(content)


def parse_raw_text(content: str) -> NormalizedDocument:
    """Parse raw text string into NormalizedDocument with precise blocks and offsets."""
    paragraphs = re.split(r'\n\s*\n', content)
    blocks: List[NormalizedBlock] = []
    
    current_offset = 0
    current_heading: Optional[str] = None

    for idx, para in enumerate(paragraphs):
        trimmed = para.strip()
        if not trimmed:
            continue

        # Check for heading
        if len(trimmed) < 80 and ("\n" not in trimmed) and not trimmed.endswith("."):
            current_heading = trimmed

        # Find actual position of trimmed text in original content
        find_pos = content.find(trimmed, current_offset)
        if find_pos != -1:
            start_offset = find_pos
            end_offset = find_pos + len(trimmed)
            current_offset = end_offset
        else:
            start_offset = current_offset
            end_offset = current_offset + len(trimmed)
            current_offset = end_offset

        blocks.append(
            NormalizedBlock(
                page_number=1,
                section_heading=current_heading,
                block_id=f"para_{idx + 1}",
                start_offset=start_offset,
                end_offset=end_offset,
                text=trimmed
            )
        )

    return NormalizedDocument(
        blocks=blocks,
        full_text=content,
        page_count=1
    )


def get_document_parser(mime_type: str) -> DocumentParserProtocol:
    if mime_type == "application/pdf":
        return PdfParser()
    elif mime_type == "text/plain":
        return PlainTextParser()
    raise ValueError(f"Unsupported mime_type: {mime_type}")

def hash_file(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

