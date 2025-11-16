# src/logic/finance.py
import pandas as pd
import math

def monthly_payment(principal, annual_rate_percent, months):
    if principal is None or months <= 0:
        return 0.0
    r = annual_rate_percent/100/12
    if r == 0:
        return principal / months
    return principal * (r * (1+r)**months) / ((1+r)**months - 1)

def amortization_schedule(principal, annual_rate, months):
    schedule = []
    r = annual_rate/100/12
    balance = principal
    payment = monthly_payment(principal, annual_rate, months)
    for m in range(1, months+1):
        interest = balance * r
        principal_paid = payment - interest
        balance -= principal_paid
        schedule.append({"month": m, "payment": payment, "interest": interest, "principal": principal_paid, "balance": max(balance,0)})
    return pd.DataFrame(schedule)

def recalc_all(session_state):
    data = session_state.get("data")
    finance = data.get("finance", {})
    income = data.get("income", {})
    collateral = data.get("collateral", [])
    principal = finance.get("so_tien_vay") or finance.get("tong_nhu_cau") or 0
    rate = finance.get("lai_suat_p_a", 8.5)
    months = int(finance.get("thoi_han_thang", 60))
    sched = amortization_schedule(principal, rate, months)
    monthly_debt_service = sched["payment"].iloc[0] if not sched.empty else 0
    annual_ds = monthly_debt_service * 12
    annual_income = (income.get("thu_nhap_hang_thang",0)) * 12
    dsr = (annual_ds/annual_income*100) if annual_income>0 else None
    coll_value = sum([c.get("gia_tri") or 0 for c in collateral])
    ltv = (principal / coll_value * 100) if coll_value>0 else None

    session_state["summary"] = {
        "monthly_payment": monthly_debt_service,
        "dsr_percent": dsr,
        "ltv_percent": ltv
    }
    return sched
