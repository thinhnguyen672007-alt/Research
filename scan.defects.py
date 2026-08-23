# scan_defects.py
import os
import re
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# BỘ REGEX PATTERN CHUẨN DÙNG CHO MÃ NGUỒN (DIFF)
# ==========================================
CONDITIONAL_REGEX = r'\b(if|switch)\s*\(.*(Output|\.apply)'
IDEMPOTENCY_REGEX = r'\b(Math\.random|Date\.now)\b'

excel_file = "Pulumi_ACID_Research_Data_Management_v1.0.xlsx"
df_commits = pd.read_excel(excel_file, sheet_name="03_COMMIT")

# Lấy token bảo mật từ môi trường hệ thống
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {"Accept": "application/vnd.github.v3.diff"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

screening_rows = []

print("=== BẮT ĐẦU SCAN SÂU BẰNG BỘ REGEX PATTERN CHUẨN TRÊN CODE DIFF ===")

for idx, row in df_commits.iterrows():
    commit_id = row["Commit_ID"]
    repo_id = row["Repository_ID"]
    commit_url = row["Commit_URL"]
    
    # Tách URL để lấy thông tin gọi API lấy file Diff
    parts = commit_url.split("/")
    owner, repo, commit_hash = parts[3], parts[4], parts[6]
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_hash}"
    res = requests.get(api_url, headers=HEADERS)
    
    if res.status_code == 200:
        diff_text = res.text
        lines = diff_text.split("\n")
        
        is_conditional_found = False
        is_idempotency_found = False
        matched_contents = []
        
        # Duyệt qua từng dòng trong nội dung diff thay đổi code
        for line in lines:
            # CHỈ QUÉT DÒNG THÊM MỚI (+) VÀ BỎ QUA DÒNG THÔNG TIN (+++)
            if line.startswith('+') and not line.startswith('+++'):
                if re.search(CONDITIONAL_REGEX, line):
                    is_conditional_found = True
                    matched_contents.append(line.strip())
                    
                if re.search(IDEMPOTENCY_REGEX, line):
                    is_idempotency_found = True
                    matched_contents.append(line.strip())
        
        # Ghi nhận kết quả nếu khớp Regex trong code
        if is_conditional_found or is_idempotency_found:
            defects = []
            if is_conditional_found: defects.append("Conditional Defect")
            if is_idempotency_found: defects.append("Idempotency Defect")
            
            defect_type = " & ".join(defects)
            combined_match = " | ".join(matched_contents)[:150]
            
            screening_rows.append({
                "Screening_ID": f"SCR-{len(screening_rows)+1:05d}",
                "Commit_ID": commit_id,
                "Repository_ID": repo_id,
                "Is_Candidate": True,
                "Candidate_Category": defect_type,
                "Keyword_Matched": combined_match,
                "Screened_By": "Auto Script (True Code Diff Regex)",
                "Screening_Date": datetime.now().strftime("%Y-%m-%d"),
                "Status": "Included",
                "Notes": "Matched advanced IaC/Pulumi regex pattern in code diff"
            })

# Ghi kết quả vào sheet 05_ACID_SCREENING trong file Excel
if screening_rows:
    with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        pd.DataFrame(screening_rows).to_excel(writer, sheet_name="05_ACID_SCREENING", index=False)
    print(f"\n=> HOÀN THÀNH! Đã dùng Regex quét sâu và tìm thấy {len(screening_rows)} candidate thực chiến.")
else:
    print("\n=> Không tìm thấy đoạn code vi phạm nào khớp với bộ Regex trong nội dung file thay đổi (diff) của các commit này.")