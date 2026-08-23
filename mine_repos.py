# mine_repos.py
import os
import requests
import pandas as pd
from datetime import datetime

try:
    from config import TEST_REPOS
except ImportError:
    TEST_REPOS = []


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

excel_file = "Pulumi_ACID_Research_Data_Management_v1.0.xlsx"


try:
    df_repo_list = pd.read_excel(excel_file, sheet_name="01_REPOSITORY_LIST")
    
except Exception as e:
    print(f"Lỗi: Không thể đọc sheet '01_REPOSITORY_LIST' từ file Excel. Hãy kiểm tra lại file! Chi tiết: {e}")
    exit()

repo_rows = []
commit_rows = []

repo_urls = df_repo_list["Repository_URL"].dropna().astype(str).tolist()
if not repo_urls:
    repo_urls = TEST_REPOS

if not repo_urls:
    print("Không có Repository_URL nào trong Excel và không có fallback trong config.py.")
    exit()

print(f"=== BẮT ĐẦU CRAWL {len(repo_urls)} REPO TỪ DANH SÁCH EXCEL ===")

for idx, url in enumerate(repo_urls, start=1):
    # Parse Owner và Repo Name từ URL
    parts = url.strip("/").split("/")
    owner, repo_name = parts[-2], parts[-1]
    
    repo_id = f"REP-{idx:05d}"
    print(f"[{idx}/{len(repo_urls)}] Đang xử lý repo: {owner}/{repo_name}...")

    # Gọi API lấy thông tin Repo
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
            "Notes": "Mining from Excel list"
        })
    else:
        print(f"   Lỗi lấy Repo {repo_name}: {res_repo.status_code}")
        continue

    # Gọi API lấy danh sách commit (ví dụ lấy 10 commit mới nhất mỗi repo)
    api_commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=10"
    res_commits = requests.get(api_commits_url, headers=HEADERS)
    
    if res_commits.status_code == 200:
        commits = res_commits.json()
        for c_idx, c in enumerate(commits, start=1):
            commit_id = f"COM-{idx:02d}{c_idx:04d}"
            commit_hash = c["sha"]
            commit_msg = c["commit"]["message"].split("\n")[0] # Lấy dòng đầu của message
            author = c["commit"]["author"]["name"]
            commit_date = c["commit"]["author"]["date"]
            
            commit_rows.append({
                "Commit_ID": commit_id,
                "Repository_ID": repo_id,
                "Commit_Hash": commit_hash,
                "Commit_URL": c["html_url"],
                "Commit_Date": commit_date,
                "Author": author,
                "Commit_Message": commit_msg,
                "Parent_Commit": c["parents"][0]["sha"] if c.get("parents") else None,
                "Branch": "main",
                "Files_Changed": 0,
                "Lines_Added": 0,
                "Lines_Deleted": 0,
                "Is_TypeScript": True,
                "Is_Pulumi_File": True,
                "Mining_Run_ID": "RUN-00001",
                "Raw_Source": "GitHub",
                "Notes": "Commit sample from list"
            })


with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
    if repo_rows:
        pd.DataFrame(repo_rows).to_excel(writer, sheet_name="02_REPOSITORY", index=False)
    if commit_rows:
        pd.DataFrame(commit_rows).to_excel(writer, sheet_name="03_COMMIT", index=False)

print("\n=> HOÀN THÀNH! Đã cào dữ liệu dựa trên danh sách repo từ Excel.")