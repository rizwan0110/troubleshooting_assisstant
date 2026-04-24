from pathlib import Path
from dataclasses import dataclass


@dataclass
class Document:
    doc_id: str
    source: str
    content: str


def load_documents(folder_path: str) -> list[Document]:
    documents = []

    folder = Path(folder_path)

    markdown_files = folder.glob("*.md")

    for index, file_path in enumerate(markdown_files, start=1):

        content = file_path.read_text(encoding="utf-8").strip()

        document = Document(
            doc_id=f"doc_{index}", source=file_path.name, content=content
        )

        documents.append(document)

    return documents
