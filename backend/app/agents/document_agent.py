"""
document agent - OCR + VLM approach. tesseract pulls raw text out of the
scanned doc/image, then an LLM call turns the messy text into actual
structured fields. went with this instead of docling/layoutlm because
those need their own model downloads and this was way faster to get working
"""
import os

from app.services import llm_service

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

EXTRACTION_PROMPT = """The following is OCR text extracted from an insurance-related document
(could be an FIR / police report, medical report, or vehicle repair estimate).
The OCR is probably a bit messy. Pull out whatever structured info you can find and
respond with ONLY a JSON object:
{{
  "doc_type_guess": "fir" | "medical_report" | "repair_estimate" | "unknown",
  "policy_number": "<if found, else null>",
  "incident_date": "<if found, else null>",
  "vehicle_number": "<if found, else null>",
  "amount_mentioned": <number if a cost/amount appears, else null>,
  "summary": "one or two sentence summary of what this document says"
}}

OCR TEXT:
{text}
"""


def _ocr_extract_text(file_path: str) -> str:
    if not OCR_AVAILABLE:
        return ""
    try:
        # only handles image-type uploads for now, pdf OCR would need pdf2image + poppler
        if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            return pytesseract.image_to_string(Image.open(file_path))
        return ""
    except Exception:
        return ""


def _mock_extraction(doc_type: str) -> dict:
    mock_amount = None
    if doc_type == "repair_estimate":
        mock_amount = 1500
    elif doc_type == "medical_report":
        mock_amount = 800

    return {
        "doc_type_guess": doc_type,
        "policy_number": "POL10234",
        "incident_date": "2026-05-14",
        "vehicle_number": "DL08CA1234",
        "amount_mentioned": mock_amount,
        "summary": f"[mock] this is a placeholder extraction for a {doc_type} document",
        "mock_mode": True,
    }


def extract_single_document(doc: dict) -> dict:
    file_path = doc["path"]
    doc_type = doc["doc_type"]

    if llm_service.is_mock():
        return {**_mock_extraction(doc_type), "doc_type": doc_type}

    raw_text = _ocr_extract_text(file_path)
    if not raw_text.strip():
        result = _mock_extraction(doc_type)
        result["summary"] = "[no readable text found in document, OCR returned empty]"
        return {**result, "doc_type": doc_type}

    try:
        result = llm_service.text_chat(EXTRACTION_PROMPT.format(text=raw_text[:3000]), json_mode=True)
        result["mock_mode"] = False
        return {**result, "doc_type": doc_type}
    except Exception as e:
        result = _mock_extraction(doc_type)
        result["error"] = str(e)
        return {**result, "doc_type": doc_type}


def extract_documents(documents: list[dict]) -> dict:
    non_photo_docs = [d for d in documents if d["doc_type"] not in ("photo", "video")]

    if not non_photo_docs:
        return {"documents": [], "notes": "no FIR/medical/repair documents were uploaded"}

    extracted = [extract_single_document(d) for d in non_photo_docs]
    return {"documents": extracted}
