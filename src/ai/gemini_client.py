# src/ai/gemini_client.py
class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze_risk(self, source_text: str, mode: str, data: dict):
        summary = []
        fin = data.get("finance", {})
        income = data.get("income", {})
        coll = data.get("collateral", [])
        loan = fin.get("so_tien_vay") or 0
        income_month = income.get("thu_nhap_hang_thang") or 0
        if income_month*12 < loan*0.5:
            summary.append("Cảnh báo: Thu nhập/năng lực trả nợ thấp so với khoản vay.")
        if coll:
            total_coll = sum([c.get("gia_tri") or 0 for c in coll])
            if total_coll < loan:
                summary.append("Cảnh báo: Giá trị tài sản đảm bảo thấp hơn số vay (LTV>100%).")
            else:
                summary.append(f"Tài sản bảo đảm đủ (tổng TSĐB = {total_coll}).")
        summary.append(f"Mode phân tích: {mode}.")
        summary.append("Gợi ý: Xem xét tăng vốn đối ứng hoặc giảm thời hạn vay để hạ DSR.")
        return "\n".join(summary)

    def chat(self, prompt: str):
        return f"[Gemini stub reply] Tôi nhận prompt: {prompt}\n(Thay bằng kết nối thật với gemini-2.5-flash.)"
