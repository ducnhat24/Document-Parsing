import streamlit as st
import pdfplumber
import easyocr
import numpy as np
import time
import cv2
from PIL import Image

st.set_page_config(layout="wide", page_title="Real AI Doc Parsing")

st.markdown("""
<style>
    .big-font { font-size:20px !important; }
    .success-box { padding:10px; background-color:#d4edda; color:#155724; border-radius:5px; margin-bottom: 10px;}
    .fail-box { padding:10px; background-color:#f8d7da; color:#721c24; border-radius:5px; margin-bottom: 10px;}
    .info-box { padding:10px; background-color:#cce5ff; color:#004085; border-radius:5px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("Real-Time Doc Parsing: Coordinate vs. Vision AI")

# --- LOAD MODEL AI ---
@st.cache_resource
def load_easyocr_model():
    reader = easyocr.Reader(['en', 'vi'], gpu=False) 
    return reader

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    parsing_mode = st.radio(
        "Select Parsing Engine:",
        ("1. Traditional (pdfplumber)", "2. Modern AI (EasyOCR Vision)")
    )
    
    st.markdown("---")
    st.caption("Hardware Status:")
    if parsing_mode == "2. Modern AI (EasyOCR Vision)":
        with st.spinner("Loading AI Model into Memory..."):
            reader = load_easyocr_model()
        st.success("AI Model Loaded (CPU Mode)")
    else:
        st.info("Using Standard CPU Library")

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 1])

uploaded_file = None

with col1:
    st.subheader("Input Document")
    uploaded_file = st.file_uploader("Drop your PDF here...", type=['pdf'])
    
    if uploaded_file:
        with pdfplumber.open(uploaded_file) as pdf:
            page = pdf.pages[0]
            im = page.to_image(resolution=200) 
            st.image(im.original, width='stretch', caption="Visual Preview")

with col2:
    st.subheader("Extraction Result")
    
    if uploaded_file and st.button("Run Parsing", width='stretch'):
        # === MODE 1: TRADITIONAL (PDFPLUMBER) ===
        if parsing_mode == "1. Traditional (pdfplumber)":
            start_time = time.time()
            with st.spinner("Analyzing Layout & Extracting Data..."):
                with pdfplumber.open(uploaded_file) as pdf:
                    page = pdf.pages[0]
                    
                    im = page.to_image(resolution=150)
                    debug_table = page.debug_tablefinder()
                    
                    if debug_table and debug_table.cells:
                        im.draw_rects(debug_table.cells, stroke="red", stroke_width=2)
                        st.image(im.annotated, caption="Visualizing Structure (Red Cells)", width='stretch')
                    else:
                        st.image(im.original, caption="Visualizing Structure: NO CELLS FOUND", width='stretch')
                        st.warning("Visual Check: pdfplumber không tìm thấy cấu trúc bảng/ô nào.")

                    table = page.extract_table() 
                    text = page.extract_text()
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    
                    if table and len(table) > 0:
                        st.markdown(f'<div class="success-box">Table Detected ({duration:.4f}s)</div>', unsafe_allow_html=True)
                        
                        import pandas as pd
                        raw_header = table[0]
                        cleaned_header = []
                        if raw_header:
                            for i, col in enumerate(raw_header):
                                col_name = f"Col_{i}" if (col is None or col == "") else str(col).replace('\n', ' ')
                                if col_name in cleaned_header: col_name = f"{col_name}_{i}"
                                cleaned_header.append(col_name)
                            
                            df = pd.DataFrame(table[1:], columns=cleaned_header)
                        else:
                            df = pd.DataFrame(table)

                        st.dataframe(df, width='stretch')
                        st.success("Analysis: Structure identified via PDF Vector Lines.")

                    elif text and len(text.strip()) > 10:
                        st.markdown(f'<div class="info-box">No Table, but Text Found ({duration:.4f}s)</div>', unsafe_allow_html=True)
                        st.text_area("Raw Text Output:", text, height=300)
                        st.info("Analysis: No table lines detected, but Text Object exists.")

                    else:
                        st.markdown(f'<div class="fail-box">EXTRACTION FAILED ({duration:.4f}s)</div>', unsafe_allow_html=True)
                        st.error("Conclusion: This is a SCANNED DOCUMENT (Image).")
                        st.markdown("""
                        **Why it failed?**
                        - No `Table Objects` (Lines/Rectangles) found.
                        - No `Text Objects` found in the PDF tree.
                        - To `pdfplumber`, this is just a blank page with a picture.
                        """)

        # === MODE 2: MODERN AI (EASYOCR VISION) ===
        else: 
            start_time = time.time()
            with st.spinner("AI Vision is analyzing pixels..."):
                
                with pdfplumber.open(uploaded_file) as pdf:
                    page = pdf.pages[0]
                    im = page.to_image(resolution=300) 
                    image_np = np.array(im.original) 

                results = reader.readtext(image_np, paragraph=True) 

                annotated_img = image_np.copy()
                
                full_text = ""
                
                for item in results:
                    bbox = item[0]
                    text = item[1]
                    
                    full_text += text + "\n\n" 
                    
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    
                    pt1 = (int(top_left[0]), int(top_left[1]))
                    pt2 = (int(bottom_right[0]), int(bottom_right[1]))
                    
                    cv2.rectangle(annotated_img, pt1, pt2, (0, 255, 0), 2)

                end_time = time.time()
                duration = end_time - start_time

                st.markdown(f'<div class="success-box">AI Vision Successful ({duration:.2f}s)</div>', unsafe_allow_html=True)
                
                st.image(annotated_img, caption="AI Vision: Detected Paragraphs (Green Boxes)", width='stretch')
                
                with st.expander("See Extracted Text"):
                    st.text(full_text)
                
                st.info(f"Analysis: AI detected {len(results)} text blocks (Paragraph Mode Enabled).")