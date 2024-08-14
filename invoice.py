import re
import pypdf

def extract_invoice_data_from_pdf(pdf_path):

    invoice_data = {}

    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = pypdf.PdfReader(pdf_file)

        # Combine text from all pages
        num_pages = len(pdf_reader.pages)
        extracted_text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            extracted_text += page.extract_text()
        print(extracted_text)
        # --- Helper Functions ---
        def extract_field(pattern, text=extracted_text):
            """Extracts a field using a regular expression pattern."""
            match = re.search(pattern, text)
            return match.group(1).strip() if match else None # return only values

        invoice_data["Invoice Number"] = extract_field(r"Invoice Number:\s*(.*)")
        invoice_data["Invoice Date"] = extract_field(r"Invoice Date:\s*(.*)")
        invoice_data["Bill to Name"] = extract_field(r"Bill To:\n(.*)\nEmployee")
        invoice_data["ID"] = extract_field(r"(?:Employee ID|Customer ID):\s*(.*)")
        invoice_data["Department"] = extract_field(r"Department:\s*(.*)")
        invoice_data["Bill to Address"] = extract_field(
            r"Department:.*\n(.*)\nDate"
        )  
        invoice_data["Subtotal"] = extract_field(
            r"Subtotal\s+(.*)"
        )  
        invoice_data["Tax"] = extract_field(r"Tax.*\s+\((.*?)\)\s+(.*)")
        invoice_data["Total Amount"] = extract_field(r"Total Amount\s(.*)")
        invoice_data["Bank Name"] = extract_field(r"Bank Name:\s*(.*)")
        invoice_data["Account Number"] = extract_field(
            r"Account Number:\s*(\d+)"
        )
        invoice_data["IFSC Code"] = extract_field(r"IFSC Code:\s*(.*)")
        if "Employability Reimbursement Invoice" in extracted_text:
            invoice_data["Type"] = "Employability Reimbursement"
        else:
            invoice_data["Type"] = "Purchase Power" 

    return invoice_data
