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


# Splits markdown by headings like #, ##, ###.
def split_markdown_into_sections(text: str) -> list[dict]:
    sections = []
    lines = text.split("\n")
    current_section = "Introduction"
    current_text = []  # always initialised before the loop

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


# If a section is too big, splits it into smaller word-based chunks.
def split_large_section(section_text: str, chunk_size: int = 500) -> list[str]:
    words = section_text.split()

    if len(words) <= chunk_size:
        return [section_text]

    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i: i + chunk_size]
        chunks.append(" ".join(chunk_words))

    return chunks


# Converts one Document into final Chunk objects with metadata.
def split_document_into_chunks(
    document: Document, chunk_size: int = 500
) -> list[Chunk]:
    chunks = []
    sections = split_markdown_into_sections(document.content)
    chunk_counter = 1

    for section in sections:
        section_title = section["section_title"]
        section_text = section["text"]

        sub_chunks = split_large_section(section_text, chunk_size=chunk_size)

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
