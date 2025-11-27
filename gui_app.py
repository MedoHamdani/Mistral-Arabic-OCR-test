import customtkinter
import tkinter
from tkinter import filedialog
import os
import base64
import threading
from mistralai import Mistral
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Set default appearance
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class OCRApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mistral OCR Tool")
        self.geometry("800x600")

        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Mistral OCR", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Language Selection
        self.language_label = customtkinter.CTkLabel(self.sidebar_frame, text="Language:", anchor="w")
        self.language_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.language_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Arabic", "English", "Mixed"])
        self.language_optionmenu.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.language_optionmenu.set("Arabic")

        # Appearance Mode
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # --- Main Area ---
        
        # File Selection Row
        self.file_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.file_frame.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)

        self.file_path_var = tkinter.StringVar()
        self.file_entry = customtkinter.CTkEntry(self.file_frame, placeholder_text="Select a file...", textvariable=self.file_path_var)
        self.file_entry.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")

        self.browse_button = customtkinter.CTkButton(self.file_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=0, pady=0)

        # Process Button
        self.process_button = customtkinter.CTkButton(self, text="Process File", command=self.start_ocr_thread)
        self.process_button.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")

        # Log/Output Area
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=2, column=1, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox.insert("0.0", "Ready to process files.\n")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Documents & Images", "*.pdf;*.jpg;*.jpeg;*.png")])
        if filename:
            self.file_path_var.set(filename)

    def log(self, message):
        self.after(0, self._log_safe, message)

    def _log_safe(self, message):
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")

    def start_ocr_thread(self):
        threading.Thread(target=self.run_ocr_process, daemon=True).start()

    def run_ocr_process(self):
        file_path = self.file_path_var.get()
        if not file_path:
            self.log("Error: Please select a file first.")
            return

        if not os.path.exists(file_path):
            self.log("Error: File not found.")
            return

        language = self.language_optionmenu.get()
        self.process_button.configure(state="disabled", text="Processing...")
        self.log("-" * 30)
        self.log(f"Starting OCR for: {os.path.basename(file_path)}")
        self.log(f"Language: {language}")

        try:
            # API Key
            api_key = "97ZQlsV45YrDusgZRwjArWGbh3nerFPb"
            client = Mistral(api_key=api_key)

            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            b64 = base64.b64encode(file_bytes).decode()
            
            # Determine mime type
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                mime_type = "application/pdf"
            elif ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif ext == ".png":
                mime_type = "image/png"
            else:
                mime_type = "application/pdf" # Default fallback

            self.log(f"Uploading ({mime_type})...")
            
            if mime_type == "application/pdf":
                document_payload = {
                    "type": "document_url",
                    "document_url": f"data:{mime_type};base64,{b64}"
                }
            else:
                # It's an image
                document_payload = {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{b64}"
                }

            resp = client.ocr.process(
                model="mistral-ocr-latest",
                document=document_payload,
                include_image_base64=True,
            )

            full_text = ""
            for page in resp.pages:
                full_text += page.markdown + "\n\n"

            # Generate Output Filenames in Downloads folder
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            filename_only = os.path.basename(file_path)
            base_name = os.path.splitext(filename_only)[0]
            
            output_md = os.path.join(downloads_path, base_name + "_output.md")
            output_txt = os.path.join(downloads_path, base_name + "_output.txt")
            output_docx = os.path.join(downloads_path, base_name + "_output.docx")
            
            self.log(f"Saving outputs to: {downloads_path}")

            # 1. Save Markdown
            with open(output_md, "w", encoding="utf-8") as f:
                f.write(full_text)
            self.log(f"Saved: {os.path.basename(output_md)}")

            # 2. Save Text
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(full_text)
            self.log(f"Saved: {os.path.basename(output_txt)}")

            # 3. Save Docx
            doc = Document()
            paragraph = doc.add_paragraph(full_text)
            
            # Handle RTL for Arabic and Mixed
            if language in ["Arabic", "Mixed"]:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                # Note: For full RTL support in Word, we'd need to set bidi properties on the run/paragraph OXML.
                # But alignment is the most visible factor.
            
            doc.save(output_docx)
            self.log(f"Saved: {os.path.basename(output_docx)}")

            self.log("Success! All files generated.")

        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            self.process_button.configure(state="normal", text="Process File")

if __name__ == "__main__":
    app = OCRApp()
    app.mainloop()
