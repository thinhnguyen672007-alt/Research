import re
import pandas as pd
from datetime import datetime


FIX_INDICATORS_REGEX = r'\b(fix|fixed|fixes|bug|issue|defect|error|incorrect|wrong|patch|resolve|resolved)\b'


CONDITIONAL_REGEX = r'\b(condition|conditional|branch|nullcheck|null-check|undefined|flag|toggle|switch|boolean)\b'
IDEMPOTENCY_REGEX = r'\b(idempotent|idempotency|rerun|re-run|retry|duplicate|already-exists|drift)\b'

excel_file = "Pulumi_ACID_Research_Data_Management_v1.0.xlsx"
df_commits = pd.read_excel(excel_file, sheet_name="03_COMMIT")

screening_rows = []

print("=== BẮT ĐẦU SCAN LỖI (ĐÃ TỐI ƯU THUẬT TOÁN ACID) ===")

for idx, row in df_commits.iterrows():
    commit_id = row["Commit_ID"]
    repo_id = row["Repository_ID"]

    commit_msg = str(row["Commit_Message"]).split("\n")[0].lower()
    

    has_fix_indicator = bool(re.search(FIX_INDICATORS_REGEX, commit_msg))
    
    if not has_fix_indicator:
        continue 
        

    is_conditional = bool(re.search(CONDITIONAL_REGEX, commit_msg))
    is_idempotency = bool(re.search(IDEMPOTENCY_REGEX, commit_msg))
    
    if is_conditional or is_idempotency:
        defect_type = "Conditional Defect" if is_conditional else "Idempotency Defect"
        matched_kw = re.search(CONDITIONAL_REGEX if is_conditional else IDEMPOTENCY_REGEX, commit_msg).group(0)
        
        screening_rows.append({
            "Screening_ID": f"SCR-{len(screening_rows)+1:05d}",
            "Commit_ID": commit_id,
            "Repository_ID": repo_id,
            "Is_Candidate": True,
            "Candidate_Category": defect_type,
            "Keyword_Matched": f"Rule: [Fix Intent + '{matched_kw}']",
            "Screened_By": "Auto Script (ACID Strict Rules)",
            "Screening_Date": datetime.now().strftime("%Y-%m-%d"),
            "Status": "Included",
            "Notes": f"Detected {defect_type} via strict pattern matching"
        })

# Ghi đè kết quả sạch vào sheet 05_ACID_SCREENING
if screening_rows:
    with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        pd.DataFrame(screening_rows).to_excel(writer, sheet_name="05_ACID_SCREENING", index=False)
    print(f"\n=> HOÀN THÀNH! Tìm thấy {len(screening_rows)} candidate thực sự chất lượng (Đã lọc bỏ False Positives).")
else:
    print("\n=> Không có commit nào vi phạm theo bộ quy tắc chặt chẽ này.")