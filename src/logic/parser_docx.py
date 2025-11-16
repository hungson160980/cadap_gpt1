# src/logic/parser_docx.py
import re
from docx import Document

def parse_docx_streamlit(uploaded_file):
    doc = Document(uploaded_file)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    identification = {}
    finance = {}
    collateral = []
    income = {}

    m = re.search(r"Họ và tên[:\s]+([A-Za-zÀ-ỹ0-9\s]+)", full_text)
    if m:
        identification["ten"] = m.group(1).strip()
    else:
        m2 = re.search(r"\d+\.\s*Họ và tên[:\s]*([^\n\r]+)", full_text)
        if m2:
            identification["ten"] = m2.group(1).strip()

    m = re.search(r"CMND/CCCD[^\d]*(\d{9,12})", full_text)
    if m:
        identification["cccd"] = m.group(1)

    m = re.search(r"Số điện thoại[:\s]*([0-9\-\+\s]{7,15})", full_text)
    if m:
        identification["phone"] = m.group(1).strip()

    m = re.search(r"Nơi cư trú[:\s]*([^\n\r]+)", full_text)
    if m:
        identification["dia_chi"] = m.group(1).strip()

    m = re.search(r"Tổng nhu cầu vốn[:\s]*([\d\.\, ]+)\s*đồng", full_text, flags=re.IGNORECASE)
    if m:
        finance["tong_nhu_cau"] = parse_vnd_number(m.group(1))
    m = re.search(r"Vốn đối ứng[:\s]*([\d\.\, ]+)\s*đồng", full_text)
    if m:
        finance["von_doi_ung"] = parse_vnd_number(m.group(1))
    m = re.search(r"Lãi suất[:\s]*([\d\.\,]+)%", full_text)
    if m:
        finance["lai_suat_p_a"] = float(m.group(1).replace(",","."))

    m = re.search(r"Vốn vay .*[:\s]*([\d\.\, ]+)\s*đồng", full_text)
    if m:
        finance["so_tien_vay"] = parse_vnd_number(m.group(1))

    m = re.search(r"Thời hạn vay[:\s]*([\d]+)\s*tháng", full_text)
    if m:
        finance["thoi_han_thang"] = int(m.group(1))

    blocks = re.split(r"\n\s*\d+\.\s+", full_text)
    for b in blocks:
        if "Tài sản" in b or "Bất động sản" in b:
            m = re.search(r"Giá trị[:\s]*([\d\.\, ]+)\s*đồng", b)
            if m:
                val = parse_vnd_number(m.group(1))
            else:
                m2 = re.search(r"Giá trị[:\s]*([0-9]+)", b)
                val = parse_vnd_number(m2.group(1)) if m2 else None
            addr = None
            m3 = re.search(r"Địa chỉ[:\s]*([^\n\r]+)", b)
            if m3:
                addr = m3.group(1).strip()
            ltv = None
            m4 = re.search(r"LTV[:\s]*([\d\.]+)%", b)
            if m4:
                ltv = float(m4.group(1))
            collateral.append({"loai":"Bất động sản","gia_tri":val,"dia_chi":addr,"ltv_percent":ltv,"giay_to":None})

    m = re.search(r"Tổng thu nhập ổn định hàng tháng[:\s]*([\d\.\, ]+)\s*đ", full_text)
    if m:
        income["thu_nhap_hang_thang"] = parse_vnd_number(m.group(1))
    m = re.search(r"Tổng chi phí hàng tháng[:\s]*([\d\.\, ]+)\s*đ", full_text)
    if m:
        income["chi_phi_hang_thang"] = parse_vnd_number(m.group(1))

    finance.setdefault("muc_dich", "Không rõ")
    finance.setdefault("tong_nhu_cau", None)
    finance.setdefault("von_doi_ung", 0)
    finance.setdefault("so_tien_vay", finance.get("tong_nhu_cau"))
    finance.setdefault("lai_suat_p_a", 8.5)
    finance.setdefault("thoi_han_thang", 60)

    return {"identification": identification, "finance": finance, "collateral": collateral, "income": income}


def parse_vnd_number(s: str):
    if not s:
        return None
    s = s.replace(".", "").replace(",", "").replace(" ", "")
    try:
        return int(s)
    except:
        try:
            return int(float(s))
        except:
            return None
