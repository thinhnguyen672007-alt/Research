
import os
import re
import requests
import pandas as pd
from datetime import datetime

#  LẤY TOKEN BẢO MẬT
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

excel_file = "Pulumi_ACID_Research_Data_Management_v1.0.xlsx"

# 2. ĐỌC DANH SÁCH REPO TỪ EXCEL (Không phụ thuộc config.py)
try:
    df_repo_list = pd.read_excel(excel_file, sheet_name="01_REPOSITORY_LIST")
    repo_urls = df_repo_list["Repository_URL"].dropna().astype(str).tolist()
except Exception as e:
    print(f"Lỗi: Không thể đọc sheet '01_REPOSITORY_LIST' từ Excel. Chi tiết: {e}")
    exit()

if not repo_urls:
    print("Danh sách Repository_URL trong Excel đang bị trống!")
    exit()


BUG_KEYWORDS_REGEX = r'\b(fix|fixed|fixes|bug|issue|defect|error|incorrect|wrong|patch|resolve|resolved|crash|fail)\b'

repo_rows = []
commit_rows = []

print(f"=== BẮT ĐẦU CRAWL VÀ LỌC BUG-FIXING COMMITS TỪ {len(repo_urls)} REPO ===")

for idx, url in enumerate(repo_urls, start=1):
    parts = url.strip("/").split("/")
    owner, repo_name = parts[-2], parts[-1]
    repo_id = f"REP-{idx:05d}"
    print(f"\n[{idx}/{len(repo_urls)}] Đang quét repo: {owner}/{repo_name}...")

    # Thu thập thông tin tổng quan Repo
    api_repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    res_repo = requests.get(api_repo_url, headers=HEADERS)
    
    if res_repo.status_code == 200:
        data_repo = res_repo.json()
        repo_rows.append({
            "Repository_ID": repo_id,
            "Repository_Name": repo_name,
            "Repository_URL": url,
            "Owner": owner,
            "Primary_Language": data_repo.get("language", "Unknown"),
            "IaC_Tool": "Pulumi",
            "IaC_Language": "TypeScript",
            "Pulumi_Version": None,
            "Repository_Status": "Eligible",
            "Mining_Run_ID": "RUN-00001",
            "Mining_Date": datetime.now().strftime("%Y-%m-%d"),
            "Notes": "Clean bug-fixing mining run with word boundary"
        })
    else:
        print(f"   Lỗi kết nối tới Repo {repo_name}: {res_repo.status_code}")
        continue

    # VÒNG LẶP PHÂN TRANG: CÀO TOÀN BỘ COMMIT LỊCH SỬ
    page = 1
    per_page = 100 
    valid_commit_count = 0

# Thêm timeout để tránh treo máy nếu mất mạng

    while True:
        api_commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page={per_page}&page={page}"
        res_commits = None
        for attempt in range(3):
            try:
                res_commits = requests.get(api_commits_url, headers=HEADERS, timeout=30)
                break
            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError):
                print(f"   Mạng chập chờn, đang thử kết nối lại lần {attempt + 1}...")
                import time
                time.sleep(2)
        
        if res_commits is None or res_commits.status_code != 200:
            print(f"   Lỗi khi lấy trang commit số {page}.")
            break
            
        commits = res_commits.json()
        
        # Thoát vòng lặp nếu API trả về mảng rỗng (đã hết lịch sử)
        if not commits:
            break
            
        print(f"   Đang quét trang {page} ({len(commits)} commits)...")
        
        for c in commits:
            commit_msg = c["commit"]["message"]
            
            # KIỂM TRA TỪ KHÓA BẰNG REGEX (Không phân biệt hoa thường)
            if re.search(BUG_KEYWORDS_REGEX, commit_msg, re.IGNORECASE):
                valid_commit_count += 1
                commit_id = f"COM-{idx:02d}{valid_commit_count:04d}"
                commit_hash = c["sha"]
                clean_msg = commit_msg.split("\n")[0]
                author = c["commit"]["author"]["name"] if c["commit"].get("author") else "Unknown"
                commit_date = c["commit"]["author"]["date"] if c["commit"].get("author") else ""
                
                commit_rows.append({
                    "Commit_ID": commit_id,
                    "Repository_ID": repo_id,
                    "Commit_Hash": commit_hash,
                    "Commit_URL": c["html_url"],
                    "Commit_Date": commit_date,
                    "Author": author,
                    "Commit_Message": clean_msg,
                    "Parent_Commit": c["parents"][0]["sha"] if c.get("parents") else None,
                    "Branch": "main",
                    "Files_Changed": 0,
                    "Lines_Added": 0,
                    "Lines_Deleted": 0,
                    # Đã gỡ bỏ cờ Is_TypeScript/Is_Pulumi ở đây để chuyển trọng trách sang file mine_commit_files.py
                    "Mining_Run_ID": "RUN-00001",
                    "Raw_Source": "GitHub",
                    "Notes": "Filtered bug-fixing commit with regex word boundary"
                })
        
        # Nếu số commit trả về ít hơn giới hạn 100, nghĩa là trang hiện tại là trang cuối cùng
        if len(commits) < per_page:
            break
            
        page += 1

    print(f"   => Đã lọc chuẩn xác {valid_commit_count} bug-fixing commits từ repo này.")

with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    if repo_rows:
        pd.DataFrame(repo_rows).to_excel(writer, sheet_name="02_REPOSITORY", index=False)
    if commit_rows:
        pd.DataFrame(commit_rows).to_excel(writer, sheet_name="03_COMMIT", index=False)

print(f"\n=> HOÀN THÀNH! Tổng cộng đã thu thập và làm sạch {len(commit_rows)} bug-fixing commits toàn hệ thống.")