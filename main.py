# main.py
import streamlit as st
from src.ui.components import sidebar_api_input, layout_tabs, format_vnd
from src.logic.parser_docx import parse_docx_streamlit
from src.logic.finance import recalc_all
from src.export.export_excel import export_schedule_excel
from src.export.export_report import build_report_pdf_docx
from src.ai.gemini_client import GeminiClient
import pandas as pd

st.set_page_config(page_title="Thẩm định phương án vay vốn", layout="wide", initial_sidebar_state="expanded")

api_key = sidebar_api_input()

uploaded = st.file_uploader("Upload file .docx (Phương án sử dụng vốn)", type=["docx"])
if "data" not in st.session_state:
    st.session_state.data = None

if uploaded is not None:
    with st.spinner("Đang phân tích file .docx ..."):
        parsed = parse_docx_streamlit(uploaded)
        st.session_state.data = parsed
        st.success("Đã trích xuất dữ liệu. Bạn có thể chỉnh sửa ở các tab.")

if st.session_state.data is None:
    sample = {
        "identification": {
            "ten": "Nguyễn Văn Minh",
            "cccd": "001085012345",
            "dia_chi": "Số 123 đường Lý Thái Tổ, Thuận Thành, Bắc Ninh",
            "phone": "0912345678",
        },
        "finance": {
            "muc_dich": "Mua nhà",
            "tong_nhu_cau": 5000000000,
            "von_doi_ung": 1000000000,
            "so_tien_vay": 5000000000,
            "lai_suat_p_a": 8.5,
            "thoi_han_thang": 60,
            "ky_tra": "tháng"
        },
        "collateral": [
            {"loai": "Bất động sản", "gia_tri": 6000000000, "dia_chi": "Lô 45, Nguyễn Văn Cừ", "ltv_percent": 83.33, "giay_to": "GCN BN 654321"}
        ],
        "income": {"thu_nhap_hang_thang": 100000000, "chi_phi_hang_thang": 45000000, "thu_nhap_du_an": 30000000},
    }
    st.session_state.data = sample
    st.info("Dùng dữ liệu mẫu (PASDV) vì chưa upload file.")

layout_tabs(st.session_state.data, recalc_callback=lambda: recalc_all(st.session_state))

st.markdown("---")
st.header("Xuất dữ liệu")
col1, col2 = st.columns(2)
with col1:
    if st.button("Xuất bảng kê kế hoạch trả nợ → Excel"):
        sched_df = recalc_all(st.session_state)
        bytes_io = export_schedule_excel(sched_df)
        st.download_button("Tải file Excel", data=bytes_io, file_name="ke_hoach_tra_no.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with col2:
    if st.button("Xuất báo cáo thẩm định → PDF & DOCX"):
        report_bytes = build_report_pdf_docx(st.session_state.data, recalc_all(st.session_state))
        st.download_button("Tải báo cáo (ZIP)", data=report_bytes, file_name="bao_cao_thamdinh.zip", mime="application/zip")

if api_key:
    client = GeminiClient(api_key)
    st.sidebar.markdown("**AI Gemini**")
    if st.sidebar.button("Phân tích AI (dựa trên File Upload)"):
        res = client.analyze_risk("Nguồn gốc: Upload", "file_upload", st.session_state.data)
        st.sidebar.text_area("Kết quả", value=res, height=200)
    if st.sidebar.button("Phân tích AI (dựa trên dữ liệu chỉnh sửa)"):
        res = client.analyze_risk("Nguồn gốc: edited", "edited", st.session_state.data)
        st.sidebar.text_area("Kết quả", value=res, height=200)

st.sidebar.markdown("---")
chat_prompt = st.sidebar.text_area("Nhập prompt chat", "")
if st.sidebar.button("Gửi (Chat)"):
    if not api_key:
        st.sidebar.error("Cần API key.")
    else:
        reply = GeminiClient(api_key).chat(chat_prompt)
        st.sidebar.text_area("Gemini trả lời", value=reply, height=150)
