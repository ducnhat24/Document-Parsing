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
            st.image(im.original, use_container_width=True, caption="Visual Preview")

with col2:
    st.subheader("Extraction Result")
    
    if uploaded_file and st.button("Run Parsing", use_container_width=True):
        
        # === MODE 1: TRADITIONAL (PDFPLUMBER) ===
        if parsing_mode == "1. Traditional (pdfplumber)":
            start_time = time.time()
            with st.spinner("Parsing PDF Object Tree..."):
                with pdfplumber.open(uploaded_file) as pdf:
                    page = pdf.pages[0]
                    # 1. Tạo ảnh visual debugging
                    im = page.to_image(resolution=150)
                    im.draw_rects(page.extract_words(), stroke="red", stroke_width=2)
                    
                    st.image(im.annotated, caption="Visualizing Bounding Boxes (How pdfplumber sees text)", use_container_width=True)
                    text = page.extract_text()
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    if text and len(text.strip()) > 5:
                        st.markdown(f'<div class="success-box">Success ({duration:.4f}s)</div>', unsafe_allow_html=True)
                        st.text_area("Raw Output:", text, height=300)
                        st.info("Analysis: Text layer detected via coordinates.")
                    else:
                        st.markdown(f'<div class="fail-box">Failed ({duration:.4f}s)</div>', unsafe_allow_html=True)
                        st.warning("Analysis: Returns Empty. No selectable text layer found.")
                        st.error("Conclusion: This is a scanned document/image. Traditional parsers cannot read it.")

        # === MODE 2: REAL AI (EASYOCR) ===
        # else: 
        #     start_time = time.time()
        #     with st.spinner("AI Vision is analyzing pixels..."):
                
        #         # 1. Chuyển PDF -> Ảnh -> Numpy Array
        #         with pdfplumber.open(uploaded_file) as pdf:
        #             page = pdf.pages[0]
        #             # Tăng độ phân giải lên 200-300 để AI nhìn rõ hơn
        #             im = page.to_image(resolution=200) 
        #             image_np = np.array(im.original) 

        #         # 2. AI Dự đoán (Lấy cả tọa độ bbox)
        #         # detail=1 (mặc định) sẽ trả về: [ [box_coords], text, confidence ]
        #         results = reader.readtext(image_np) 

        #         # 3. Vẽ Bounding Box lên ảnh để Visualize
        #         # Copy ảnh ra để vẽ (tránh làm hỏng ảnh gốc)
        #         annotated_img = image_np.copy()
                
        #         full_text = ""
        #         for (bbox, text, prob) in results:
        #             full_text += text + "\n"
                    
        #             # Lấy tọa độ 4 góc (EasyOCR trả về danh sách 4 điểm)
        #             # bbox = [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        #             (top_left, top_right, bottom_right, bottom_left) = bbox
                    
        #             # Chuyển về dạng số nguyên (int) để vẽ
        #             pt1 = (int(top_left[0]), int(top_left[1]))
        #             pt2 = (int(bottom_right[0]), int(bottom_right[1]))
                    
        #             # Vẽ hình chữ nhật MÀU XANH LÁ (Green)
        #             # Tham số: ảnh, điểm đầu, điểm cuối, màu (R,G,B), độ dày
        #             cv2.rectangle(annotated_img, pt1, pt2, (0, 255, 0), 2)

        #         end_time = time.time()
        #         duration = end_time - start_time

        #         # 4. Hiển thị kết quả
        #         st.markdown(f'<div class="success-box">AI Vision Successful ({duration:.2f}s)</div>', unsafe_allow_html=True)
                
        #         # Hiển thị ảnh ĐÃ VẼ KHUNG (Visual Proof)
        #         st.image(annotated_img, caption="AI Vision: Detected Text Patterns (Green Boxes)", use_container_width=True)
                
        #         # Hiển thị Text
        #         with st.expander("See Extracted Text"):
        #             st.text(full_text)
                
        #         st.info(f"Analysis: AI detected {len(results)} text regions based on visual shapes.")
        else: 
            start_time = time.time()
            with st.spinner("AI Vision is analyzing pixels..."):
                
                # 1. Chuyển PDF -> Ảnh -> Numpy Array
                with pdfplumber.open(uploaded_file) as pdf:
                    page = pdf.pages[0]
                    # Tăng độ phân giải lên 300 để đọc chữ nhỏ tốt hơn
                    im = page.to_image(resolution=300) 
                    image_np = np.array(im.original) 

                # 2. AI Dự đoán (CÓ PARAGRAPH=TRUE)
                # Lưu ý: Khi thêm paragraph=True, EasyOCR sẽ tự động nối các dòng gần nhau
                # Kết quả trả về sẽ mất đi biến 'probability' (độ tin cậy)
                results = reader.readtext(image_np, paragraph=True) 

                # 3. Vẽ Bounding Box lên ảnh để Visualize
                annotated_img = image_np.copy()
                
                full_text = ""
                
                for item in results:
                    # Khi paragraph=True, item chỉ có 2 phần tử: [bbox, text]
                    bbox = item[0]
                    text = item[1]
                    
                    full_text += text + "\n\n" # Thêm 2 dấu xuống dòng để tách đoạn cho rõ
                    
                    # Xử lý tọa độ để vẽ
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    
                    pt1 = (int(top_left[0]), int(top_left[1]))
                    pt2 = (int(bottom_right[0]), int(bottom_right[1]))
                    
                    # Vẽ khung màu xanh lá
                    cv2.rectangle(annotated_img, pt1, pt2, (0, 255, 0), 2)

                end_time = time.time()
                duration = end_time - start_time

                # 4. Hiển thị kết quả
                st.markdown(f'<div class="success-box">AI Vision Successful ({duration:.2f}s)</div>', unsafe_allow_html=True)
                
                st.image(annotated_img, caption="AI Vision: Detected Paragraphs (Green Boxes)", use_container_width=True)
                
                with st.expander("See Extracted Text"):
                    st.text(full_text)
                
                st.info(f"Analysis: AI detected {len(results)} text blocks (Paragraph Mode Enabled).")