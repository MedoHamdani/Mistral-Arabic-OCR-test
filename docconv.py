import base64
import sys
sys.stdout.reconfigure(encoding='utf-8')
from mistralai import Mistral
import arabic_reshaper
from bidi.algorithm import get_display

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

with open("output.md", "w", encoding="utf-8") as out_file:
    for page in resp.pages:
        # Save original (logical) text to file - this works for copy-pasting/documents
        out_file.write(page.markdown + "\n\n")

        # Reshape for terminal display only - this works for viewing in the console
        reshaped_text = arabic_reshaper.reshape(page.markdown)
        bidi_text = get_display(reshaped_text)
        print(bidi_text)
