import io
import re
from typing import List, Dict, Any, Tuple
from docx import Document
from contract_app.infrastructure.storage.file_storage import file_storage
from contract_app.modules.revisions.domain.revision_plan import RevisionPlan

class DocxService:
    def extract_structure(self, object_key: str) -> List[Dict[str, Any]]:
        raw_bytes = file_storage.read_file(object_key)
        doc = Document(io.BytesIO(raw_bytes))
        blocks: List[Dict[str, Any]] = []

        para_idx = 0
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            para_idx += 1
            # Match clause number e.g. "第一条", "1.1", "第3条"
            m = re.match(r'^(第[一二三四五六七八九十0-9]+条|\d+(\.\d+)*)\s*(.*)', text)
            clause_num = m.group(1) if m else f"段落 {para_idx}"
            blocks.append({
                "block_id": f"blk_{para_idx}",
                "clause_id": clause_num,
                "text": text,
                "length": len(text)
            })
        return blocks

    def create_sample_docx(self, title: str, paragraphs: List[str]) -> Tuple[str, str]:
        doc = Document()
        doc.add_heading(title, level=1)
        for p in paragraphs:
            doc.add_paragraph(p)
        buf = io.BytesIO()
        doc.save(buf)
        raw = buf.getvalue()
        return file_storage.save_file(raw, f"{title}.docx")

    def apply_revision_plan(
        self,
        base_object_key: str,
        plan: RevisionPlan,
        clean: bool = False
    ) -> Tuple[str, str]:
        raw_bytes = file_storage.read_file(base_object_key)
        doc = Document(io.BytesIO(raw_bytes))

        # Build replacement mapping from operations
        replacements = {}
        for op in plan.operations:
            if clean and op.status == "rejected":
                continue
            if op.expected_text:
                replacements[op.expected_text.strip()] = op.replacement_text.strip()

        for p in doc.paragraphs:
            text = p.text
            for exp, rep in replacements.items():
                if exp in text:
                    p.text = text.replace(exp, rep)
                    text = p.text

        buf = io.BytesIO()
        doc.save(buf)
        raw = buf.getvalue()
        suffix = "_clean.docx" if clean else "_proposed.docx"
        return file_storage.save_file(raw, f"rev_{plan.id}{suffix}")

docx_service = DocxService()
