import re
import os
from typing import List, Dict
from io import BytesIO
from urllib.parse import urlparse

import pdfplumber
import requests
from langchain_text_splitters import RecursiveCharacterTextSplitter


def download_pdf_from_url(url: str) -> BytesIO:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download PDF: {response.status_code}")
    return BytesIO(response.content)


def smart_chunk_text(text: str, chunk_size=1000, chunk_overlap=200) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_text(text)


def extract_policy_name(text: str) -> str:
    matches = re.findall(r"\b(?:[A-Z][a-z]+\s?){1,6}Policy\b", text)
    blacklist = {"Policyholder", "Policy Terms", "Policy Document", "Policy Year", "Policy Period"}

    for match in matches:
        if all(bad not in match for bad in blacklist):
            return match.strip()

    return None


def extract_text_chunks_with_metadata(
    pdfurl: str,
    pdf_path: BytesIO,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> List[Dict]:
    chunks = []
    chunk_id = 0
    current_policy = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            cleaned_text = re.sub(r"\n+", " ", text).strip()
            cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)

            detected_policy = extract_policy_name(cleaned_text)
            if detected_policy:
                current_policy = detected_policy

            chunked_texts = smart_chunk_text(cleaned_text, chunk_size, overlap)

            for chunk in chunked_texts:
                policy_tagged_chunk = f"[Policy: {current_policy}]\n{chunk}" if current_policy else chunk
                chunks.append(
                    {
                        "source": os.path.basename(urlparse(pdfurl).path),
                        "page": page_number,
                        "chunk_id": chunk_id,
                        "policy": current_policy,
                        "content": policy_tagged_chunk,
                    }
                )
                chunk_id += 1

    return chunks
