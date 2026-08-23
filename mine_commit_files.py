# mine_commit_files.py
import os
import requests
import pandas as pd

# Lấy token bảo mật từ biến môi trường
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

excel_file = "Pulumi_ACID_Research_Data_Management_v1.0.xlsx"
df_commits = pd.read_excel(excel_file, sheet_name="03_COMMIT")

HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

commit_file_rows = []

print("=== BẮT ĐẦU CRAWL FILE CHI TIẾT TỪ CÁC COMMIT ===")

for idx, row in df_commits.iterrows():
    commit_id = row["Commit_ID"]
    commit_url = row["Commit_URL"]
    
    # Parse owner, repo, commit_hash từ URL
    parts = commit_url.split("/")
    owner, repo, commit_hash = parts[3], parts[4], parts[6]
    
    print(f"[{idx+1}/{len(df_commits)}] Lấy file sửa đổi của Commit {commit_id}...")
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_hash}"
    res = requests.get(api_url, headers=HEADERS)
    
    if res.status_code == 200:
        files = res.json().get("files", [])
        for f_idx, f in enumerate(files, start=1):
            filename = f["filename"]
            is_ts = filename.endswith(".ts") or filename.endswith(".tsx")
            is_pulumi = "pulumi" in filename.lower() or filename.endswith("Pulumi.yaml") or is_ts
            
            commit_file_rows.append({
                "Commit_File_ID": f"FILE-{idx+1:02d}{f_idx:04d}",
                "Commit_ID": commit_id,
                "File_Path": filename,
                "File_Extension": f".{filename.split('.')[-1]}" if "." in filename else "",
                "Is_TypeScript": is_ts,
                "Is_Pulumi_File": is_pulumi,
                "Lines_Added": f.get("additions", 0),
                "Lines_Deleted": f.get("deletions", 0),
                "Change_Type": f.get("status", "modified").capitalize(),
                "Before_File_Available": True,
                "After_File_Available": True,
                "Notes": "Pilot mining commit file"
            })

# Ghi bổ sung vào sheet 04_COMMIT_FILE
with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
    pd.DataFrame(commit_file_rows).to_excel(writer, sheet_name="04_COMMIT_FILE", index=False)

print("\n=> HOÀN THÀNH! Đã ghi xong dữ liệu vào sheet 04_COMMIT_FILE.")