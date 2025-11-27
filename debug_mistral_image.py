from mistralai import Mistral
import base64
import os

api_key = "97ZQlsV45YrDusgZRwjArWGbh3nerFPb"
client = Mistral(api_key=api_key)

# Create a tiny dummy PNG base64
dummy_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

print("--- Test 1: type='image_url', mime='image/png' ---")
try:
    resp = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": f"data:image/png;base64,{dummy_png_b64}"
        }
    )
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")

print("\n--- Test 2: type='document_url', mime='image/png' (Current Code) ---")
try:
    resp = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:image/png;base64,{dummy_png_b64}"
        }
    )
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")

print("\n--- Test 3: type='document_url', mime='application/pdf' (Spoofing) ---")
try:
    resp = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{dummy_png_b64}"
        }
    )
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
