from dataclasses import dataclass
from typing import Optional
from app.utils.document_loader import Document


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    source: str
    section_title: str
    text: str
    chunk_index: int
    embedding: Optional[list[float]] = None


def split_markdown_into_sections(text: str) -> list[dict]:
    """Splits markdown by headings like #, ##, ###."""
    sections = []
    lines = text.split("\n")
    current_section = "Introduction"
    current_text = []

    for line in lines:
        if line.startswith("#"):
            if current_text:
                section_text = "\n".join(current_text).strip()
                if section_text:
                    sections.append(
                        {
                            "section_title": current_section,
                            "text": section_text,
                        }
                    )
            current_section = line.strip()
            current_text = []
        else:
            current_text.append(line)

    if current_text:
        section_text = "\n".join(current_text).strip()
        if section_text:
            sections.append(
                {
                    "section_title": current_section,
                    "text": section_text,
                }
            )

    return sections


def split_large_section(
    section_text: str,
    section_title: str,  # FIX 2: accept title so we can prepend it
    chunk_size: int = 500,
    overlap: int = 100,  # FIX 1: overlap added
) -> list[str]:
    """
    If a section is too big, splits it into overlapping word-based chunks.
    Each chunk is prefixed with the section title for better retrieval.
    """
    words = section_text.split()
    title_prefix = f"{section_title}\n\n"

    if len(words) <= chunk_size:
        # FIX 2: prepend title even for single-chunk sections
        return [title_prefix + section_text]

    chunks = []
    step = chunk_size - overlap  # FIX 1: slide by (chunk_size - overlap)

    for i in range(0, len(words), step):
        chunk_words = words[i: i + chunk_size]
        if chunk_words:
            # FIX 2: prepend section title into every chunk's text
            chunks.append(title_prefix + " ".join(chunk_words))

        # Stop if we've consumed all words
        if i + chunk_size >= len(words):
            break

    return chunks


def split_document_into_chunks(
    document: Document,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[Chunk]:
    """Converts one Document into final Chunk objects with metadata."""
    chunks = []
    sections = split_markdown_into_sections(document.content)
    chunk_counter = 1

    for section in sections:
        section_title = section["section_title"]
        section_text = section["text"]

        sub_chunks = split_large_section(
            section_text,
            section_title=section_title,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_text in sub_chunks:
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}_chunk_{chunk_counter}",
                    doc_id=document.doc_id,
                    source=document.source,
                    section_title=section_title,
                    text=chunk_text,
                    chunk_index=chunk_counter,
                )
            )
            chunk_counter += 1

    return chunks
