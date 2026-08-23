import re
# 1. Pattern quét lỗi Idempotency:

REGEX_IDEMPOTENCY = r'\b(Math\.random|Date\.now)\b'

# 2. Pattern quét lỗi Conditional:
# Tìm câu lệnh if/switch kết hợp với biến Output hoặc hàm .apply() đặc thù của Pulumi TypeScript
REGEX_CONDITIONAL = r'\b(if|switch)\s*\(.*(Output|\.apply)'

match_count = 0


def test_regex_patterns(code_line):
    print(f"Đang kiểm tra dòng code: '{code_line}'")
    
    match_idem = re.search(REGEX_IDEMPOTENCY, code_line)
    match_cond = re.search(REGEX_CONDITIONAL, code_line)
    
    if match_idem:
        print(f"  -> [BẮT ĐƯỢC LỖI IDEMPOTENCY]: Khớp với từ khóa '{match_idem.group(0)}'")
        match_count+= 1
    if match_cond:
        print(f"  -> [BẮT ĐƯỢC LỖI CONDITIONAL]: Khớp với cấu trúc rẽ nhánh Output/apply")
        match_count+= 1

    if not match_idem and not match_cond:
        print("  -> (Sạch, không dính lỗi)")
    print("-" * 40)

# Chạy thử nghiệm với các dòng code mẫu:
test_regex_patterns("+ const randomId = Math.random();")
test_regex_patterns("+ if (server.ip.apply(ip => ip === '1.2.3.4')) { createBucket(); }")
test_regex_patterns("+ const normalVar = 'Hello World';")