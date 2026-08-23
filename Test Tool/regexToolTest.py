import requests as rq
import re


owner = "pulumi"
repo = "pulumi-awsx"
commit_code = "918acb22e388a5fa81f4e62e34f9aa945a7abe3e"


url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_code}"

#CẤU HÌNH HEADER ĐỂ YÊU CẦU TRẢ VỀ DIFF VÀ CÓ USER-AGENT
headers = {
    "Accept": "application/vnd.github.v3.diff",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}



print("Đang gửi yêu cầu GET đến GitHub API để lấy file Diff...")
response = rq.get(url, headers=headers)

if response.status_code == 200:
    diff_text = response.text
    print("\n=== KẾT QUẢ THÀNH CÔNG! ĐÂY LÀ NỘI DUNG DIFF THẬT ===")

    lines = diff_text.split("\n")

    # Pattern tìm lỗi Idempotency (chứa Math.random hoặc Date.now)
    regex_idempotency = r'\b(Math\.random|Date\.now)\b'
    
    # Pattern tìm lỗi Conditional (chứa lệnh if kết hợp với biến Output hoặc .apply)
    regex_conditional = r'\bif\s*\(.*(Output|\.apply)'

    match_count = 0 

    for idx, line in enumerate(lines):  
        if line.startswith('+') and not line.startswith('+++'):
            
            # Kiểm tra xem dòng code mới có dính lỗi Idempotency không
            if re.search(regex_idempotency, line):
                match_count += 1
                print(f"[CẢNH BÁO LỖI IDEMPOTENCY] Dòng {idx+1}: {line}")
                
            # Kiểm tra xem dòng code mới có dính lỗi Conditional không
            if re.search(regex_conditional, line):
                match_count += 1
                print(f"[CẢNH BÁO LỖI CONDITIONAL] Dòng {idx+1}: {line}")

    print(f"\nQuét hoàn tất! Tìm thấy {match_count} điểm nghi vấn (candidates) khớp với Regex.")
else:
    print(f"Lỗi kết nối: {response.status_code}")