# src/export/export_excel.py
import io
import pandas as pd

def export_schedule_excel(df):
    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Schedule")
    towrite.seek(0)
    return towrite.getvalue()
