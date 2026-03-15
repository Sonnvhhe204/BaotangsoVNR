import os
import platform
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


def ping_ip(ip):
    """Gửi 1 gói tin ping để kiểm tra trạng thái IP"""
    # Lệnh ping khác nhau giữa Windows và Linux/Mac
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = (
        f"ping {param} 1 -w 1000 {ip} > nul"
        if platform.system().lower() == "windows"
        else f"ping {param} 1 -W 1 {ip} > /dev/null"
    )

    response = os.system(command)
    return "On" if response == 0 else "Off"


def scan_range(start_last_octet, end_last_octet):
    """Quét dải IP từ 100 đến 250"""
    ips = [f"192.168.1.{i}" for i in range(start_last_octet, end_last_octet + 1)]
    results = []

    print(f"--- Đang quét dải IP từ {start_last_octet} đến {end_last_octet} ---")

    # Sử dụng ThreadPoolExecutor để ping nhanh (song song)
    with ThreadPoolExecutor(max_workers=50) as executor:
        status_list = list(executor.map(ping_ip, ips))

    for ip, status in zip(ips, status_list):
        results.append({"IP": ip, "Trạng thái": status})

    return pd.DataFrame(results)


if __name__ == "__main__":
    # LẦN 1: Quét và lưu file
    print("Bắt đầu quét LẦN 1...")
    df1 = scan_range(1, 250)
    df1.to_excel("lan_check_1.xlsx", index=False)
    print("Đã lưu: lan_check_1.xlsx")

    input("\n[HÀNH ĐỘNG]: Hãy rút/cắm thiết bị rồi nhấn Enter để quét LẦN 2...")

    # LẦN 2: Quét và lưu file
    print("Bắt đầu quét LẦN 2...")
    df2 = scan_range(1, 250)
    df2.to_excel("lan_check_2.xlsx", index=False)
    print("Đã lưu: lan_check_2.xlsx")

    # SO SÁNH
    print("\n--- Đang tiến hành so sánh thay đổi ---")
    comparison = df1.copy()
    comparison.columns = ["IP", "Lần 1"]
    comparison["Lần 2"] = df2["Trạng thái"]

    # Xác định sự thay đổi
    def check_change(row):
        if row["Lần 1"] == "On" and row["Lần 2"] == "Off":
            return "Bị rút ra (Ngắt kết nối)"
        elif row["Lần 1"] == "Off" and row["Lần 2"] == "On":
            return "Mới cắm vào (Kết nối mới)"
        else:
            return "Không đổi"

    comparison["Thay đổi"] = comparison.apply(check_change, axis=1)

    # Chỉ lưu những IP có sự thay đổi để dễ quan sát
    changes_only = comparison[comparison["Thay đổi"] != "Không đổi"]

    with pd.ExcelWriter("so_sanh_thay_doi.xlsx") as writer:
        comparison.to_excel(writer, sheet_name="Tất cả IP", index=False)
        changes_only.to_excel(writer, sheet_name="Chỉ các thay đổi", index=False)

    print("--- HOÀN TẤT ---")
    print("Kết quả so sánh đã được lưu vào file: so_sanh_thay_doi.xlsx")
