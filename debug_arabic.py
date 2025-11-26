import arabic_reshaper
from bidi.algorithm import get_display
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

text = "سلام" # Salam (Sin, Lam, Alif, Mim)

print("--- Test 1: Raw (Logical) ---")
print(text)

print("\n--- Test 2: Reshaped Only (Logical) ---")
reshaped_text = arabic_reshaper.reshape(text)
print(reshaped_text)

print("\n--- Test 3: Reshaped + Bidi (Visual/Reversed) ---")
bidi_text = get_display(reshaped_text)
print(bidi_text)
