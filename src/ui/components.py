# src/ui/components.py
import streamlit as st
from src.logic.finance import recalc_all
import math

def format_vnd(n):
    try:
        return f"{int(n):,}".replace(",",".")
    except:
        return n

def sidebar_api_input():
    st.sidebar.title("Cấu hình")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    return api_key

def number_spinner(label, key, value, step=1, min_value=None, max_value=None):
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("-", key=key+"-minus"):
            value = (value or 0) - step
    with col2:
        v = st.number_input(label, value=value or 0, step=step, key=key)
    with col3:
        if st.button("+", key=key+"-plus"):
            v = v + step
    return v

def layout_tabs(data, recalc_callback):
    tabs = st.tabs([
        "1. Thông tin định danh 🧾",
        "2. Thông tin tài chính 💰",
        "3. Tài sản bảo đảm 🏠",
        "4. Tính toán & Dòng tiền 📊",
        "5. Biểu đồ 📈",
        "6. Phân tích AI 🔎",
        "7. Chatbox 💬",
        "8. Xuất file ⤓"
    ])
    # Tab 1
    with tabs[0]:
        st.header("Thông tin định danh khách hàng")
        idf = data.get("identification", {})
        idf["ten"] = st.text_input("Họ và tên", value=idf.get("ten",""))
        idf["cccd"] = st.text_input("CCCD/CMND", value=idf.get("cccd",""))
        idf["dia_chi"] = st.text_area("Địa chỉ", value=idf.get("dia_chi",""))
        idf["phone"] = st.text_input("Số điện thoại", value=idf.get("phone",""))
        data["identification"] = idf

    # Tab 2
    with tabs[1]:
        st.header("Thông tin tài chính / Phương án sử dụng vốn")
        fin = data.get("finance", {})
        fin["muc_dich"] = st.text_input("Mục đích vay", value=fin.get("muc_dich",""))
        fin["tong_nhu_cau"] = st.number_input("Tổng nhu cầu vốn (đồng)", value=fin.get("tong_nhu_cau") or 0, step=1000000, format="%d")
        fin["von_doi_ung"] = st.number_input("Vốn đối ứng (đồng)", value=fin.get("von_doi_ung") or 0, step=1000000, format="%d")
        fin["so_tien_vay"] = st.number_input("Số tiền vay (đồng)", value=fin.get("so_tien_vay") or fin.get("tong_nhu_cau") or 0, step=1000000, format="%d")
        fin["lai_suat_p_a"] = st.number_input("Lãi suất (%/năm)", value=float(fin.get("lai_suat_p_a") or 8.5), step=0.1, format="%.2f")
        fin["thoi_han_thang"] = st.number_input("Thời hạn (tháng)", value=int(fin.get("thoi_han_thang") or 60), step=1)
        data["finance"] = fin

    # Tab 3
    with tabs[2]:
        st.header("Tài sản bảo đảm")
        coll = data.get("collateral", [])
        for i, c in enumerate(coll):
            st.subheader(f"Tài sản {i+1}")
            c["loai"] = st.text_input(f"Loại tài sản ##{i+1}", value=c.get("loai",""))
            c["gia_tri"] = st.number_input(f"Giá trị (đồng) #{i+1}", value=c.get("gia_tri") or 0, step=1000000, format="%d")
            c["dia_chi"] = st.text_input(f"Địa chỉ #{i+1}", value=c.get("dia_chi",""))
            c["ltv_percent"] = st.number_input(f"LTV (%) #{i+1}", value=c.get("ltv_percent") or 0.0, step=0.1, format="%.2f")
            c["giay_to"] = st.text_input(f"Giấy tờ pháp lý #{i+1}", value=c.get("giay_to",""))
        if st.button("Thêm tài sản"):
            coll.append({"loai":"","gia_tri":0,"dia_chi":"","ltv_percent":0.0,"giay_to":""})
        data["collateral"] = coll

    # Tab 4: Tính toán
    with tabs[3]:
        st.header("Tính toán chỉ tiêu tài chính / Dòng tiền")
        sched = recalc_callback()
        st.subheader("Tổng quan")
        summary = st.session_state.get("summary", {})
        st.write("Thanh toán hàng tháng:", format_vnd(round(summary.get("monthly_payment",0))))
        st.write("DSR (ước tính %):", f"{summary.get('dsr_percent'):.2f}%" if summary.get("dsr_percent") else "Không có dữ liệu")
        st.write("LTV (ước tính %):", f"{summary.get('ltv_percent'):.2f}%" if summary.get("ltv_percent") else "Không có dữ liệu")
        st.subheader("Lịch trả nợ (một vài dòng đầu)")
        st.dataframe(sched.head(12).assign(payment=lambda df: df["payment"].apply(lambda x: f"{int(x):,}".replace(",","."))))

    # Tab 5: Biểu đồ
    with tabs[4]:
        st.header("Biểu đồ")
        import matplotlib.pyplot as plt
        sched = recalc_callback()
        if not sched.empty:
            fig, ax = plt.subplots()
            ax.plot(sched["month"], sched["payment"])
            ax.set_title("Nghĩa vụ trả nợ hàng tháng")
            ax.set_xlabel("Tháng")
            ax.set_ylabel("Số tiền (đồng)")
            st.pyplot(fig)

    # Tabs 6 & 7 & 8 left minimal as sidebar AI does heavy lifting
    with tabs[5]:
        st.header("Phân tích AI (Tab tóm tắt)")
        st.write("Sử dụng thanh bên để gọi Gemini phân tích (dựa vào file upload hoặc dữ liệu đã chỉnh sửa).")

    with tabs[6]:
        st.header("Chatbox Gemini")
        st.write("Sử dụng Chatbox ở sidebar.")

    with tabs[7]:
        st.header("Xuất file")
        st.write("Các nút xuất đặt ở cuối trang chính (dưới).")

