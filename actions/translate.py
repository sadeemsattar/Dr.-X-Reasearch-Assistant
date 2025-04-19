
import docx
import fitz  # PyMuPDF
import pandas as pd
import os
from typing import Optional
from deep_translator import GoogleTranslator

class StructuredFileTranslator:
    def __init__(self, file_path: str, source_lang: str = "auto", target_lang: str = "en"):
        self.file_path = file_path
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.file_type = self._detect_file_type()
        self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)

    def _detect_file_type(self):
        ext = os.path.splitext(self.file_path)[-1].lower()
        return {
            ".txt": "text/plain",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".csv": "text/csv",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }.get(ext, None)

    def translate(self) -> Optional[str]:
        if self.file_type == "application/pdf":
            return self._translate_pdf()
        elif self.file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self._translate_docx()
        elif self.file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return self._translate_excel()
        elif self.file_type == "text/csv":
            return self._translate_csv()
        elif self.file_type == "text/plain":
            return self._translate_text()
        else:
            raise ValueError("Unsupported file type")

    def _translate_text(self):
        out_path = self.file_path.replace(".txt", f"_translated_{self.target_lang}.txt")
        with open(self.file_path, "r", encoding="utf-8") as infile, open(out_path, "w", encoding="utf-8") as outfile:
            for line in infile:
                translated = self.translator.translate(line.strip())
                outfile.write(translated + "\n")
        return out_path

    def _translate_csv(self):
        df = pd.read_csv(self.file_path)
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).apply(lambda x: self.translator.translate(x) if x.strip() else x)
        out_path = self.file_path.replace(".csv", f"_translated_{self.target_lang}.csv")
        df.to_csv(out_path, index=False)
        return out_path

    def _translate_excel(self):
        df = pd.read_excel(self.file_path, sheet_name=None)
        output_path = self.file_path.replace(".xlsx", f"_translated_{self.target_lang}.xlsx")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, sheet_data in df.items():
                for col in sheet_data.columns:
                    if sheet_data[col].dtype == object:
                        sheet_data[col] = sheet_data[col].astype(str).apply(lambda x: self.translator.translate(x) if x.strip() else x)
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
        return output_path

    def _translate_docx(self):
        doc = docx.Document(self.file_path)
        for para in doc.paragraphs:
            if para.text.strip():
                para.text = self.translator.translate(para.text)
        out_path = self.file_path.replace(".docx", f"_translated_{self.target_lang}.docx")
        doc.save(out_path)
        return out_path

    def _translate_pdf(self):
        doc = fitz.open(self.file_path)
        out_path = self.file_path.replace(".pdf", f"_translated_{self.target_lang}.pdf")
        WHITE = fitz.pdfcolor["white"]
        textflags = fitz.TEXT_DEHYPHENATE
        ocg_xref = doc.add_ocg("Translated", on=True)

        for page in doc:
            blocks = page.get_text("blocks", flags=textflags)
            for block in blocks:
                bbox, text = block[:4], block[4].strip()
                if not text:
                    continue
                translated = self.translator.translate(text)
                page.draw_rect(bbox, color=None, fill=WHITE, oc=ocg_xref)
                page.insert_htmlbox(bbox, translated, css="* {font-family: sans-serif;}", oc=ocg_xref)

        doc.subset_fonts()
        doc.ez_save(out_path)
        return out_path
