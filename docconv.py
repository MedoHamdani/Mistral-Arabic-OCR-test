import base64
import sys
sys.stdout.reconfigure(encoding='utf-8')
from mistralai import Mistral
import arabic_reshaper
from bidi.algorithm import get_display
from docx import Document

with open("document.pdf", "rb") as f:
    pdf_bytes = f.read()

b64 = base64.b64encode(pdf_bytes).decode()
client = Mistral(api_key="97ZQlsV45YrDusgZRwjArWGbh3nerFPb")

resp = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{b64}"
    },
    include_image_base64=True,
)

# Collect all text first
full_text = ""
for page in resp.pages:
    full_text += page.markdown + "\n\n"

# 1. Save to Markdown (Logical Order)
with open("output.md", "w", encoding="utf-8") as f:
    f.write(full_text)

# 2. Save to Text File (Logical Order)
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

# 3. Save to Word Document (Logical Order)
doc = Document()
# Add a paragraph with the text. 
# Note: For proper Arabic support in Word, complex scripts usually handle themselves, 
# but setting the paragraph direction to RTL is often helpful. 
# For simplicity, we just dump the text which Word usually detects correctly.
doc.add_paragraph(full_text)
doc.save("output.docx")

# 4. Print to Terminal (Visual Order for Console)
# We process page by page for the terminal to stream output if needed, 
# or just print the full text. Let's stick to page-by-page to match previous behavior.
for page in resp.pages:
    reshaped_text = arabic_reshaper.reshape(page.markdown)
    bidi_text = get_display(reshaped_text)
    print(bidi_text)
