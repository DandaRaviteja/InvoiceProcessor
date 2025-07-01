import streamlit as st
import base64
import fitz  # PyMuPDF
from PIL import Image
from pyzbar.pyzbar import decode
import io
import json
import jwt as pyjwt  # Ensure PyJWT is used
from PyPDF2 import PdfMerger


st.set_page_config(page_title="Invoice Processor", layout="wide")

def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def extract_qr_from_pdf(uploaded_file):
    qr_results = []
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        zoom = 3
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        decoded_objs = decode(img)
        for obj in decoded_objs:
            qr_results.append(obj.data.decode("utf-8"))
    return qr_results

def decode_gst_qr_string(qr_strings):
    results = []
    for qr_string in qr_strings:
        try:
            decoded_data = pyjwt.decode(qr_string, options={"verify_signature": False})
            data_field = decoded_data.get("data", "{}")
            invoice_data = json.loads(data_field)
            results.append(invoice_data)
        except Exception as e:
            results.append({"Error": f"Failed to decode QR: {str(e)}"})
    if not results:
        results.append({"Info": "No QR code data decoded"})
    return results


def combine_pdfs(files):
    merger = PdfMerger()
    for pdf in files:
        merger.append(pdf)
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return output


# --- UI ---
st.markdown(
    "<h1 style='text-align: center;'>📄 Invoice Processor</h1>", 
    unsafe_allow_html=True
)

left_col, right_col = st.columns([1, 3])

with left_col:
    st.subheader("PDF Viewer")
    pdf_file = st.file_uploader("Upload file to view PDF", type="pdf")
    
    st.subheader("QR Extractor")
    qr_file = st.file_uploader("Upload file for QR extraction", type="pdf")

    st.subheader("PDF Combiner")
    combine_files = st.file_uploader("Upload multiple PDFs to combine", type="pdf", accept_multiple_files=True)
    if combine_files and st.button("Combine PDFs"):
        combined_pdf = combine_pdfs(combine_files)
        st.success("PDFs combined successfully!")
        st.download_button("Download Combined PDF", combined_pdf, file_name="combined.pdf", mime="application/pdf")

with right_col:
    if pdf_file:
        pdf_file.seek(0)
        display_pdf(pdf_file)

    if qr_file:
        st.info("Scanning for QR codes...")
        qr_file.seek(0)
        qr_strings = extract_qr_from_pdf(qr_file)
        if qr_strings:
            gst_data_list = decode_gst_qr_string(qr_strings)
            for idx, data in enumerate(gst_data_list):
                st.success(f"QR {idx + 1} GST Details:\n{json.dumps(data, indent=2)}")
        else:
            st.warning("No QR code detected. Try uploading a clearer or higher-quality PDF.")