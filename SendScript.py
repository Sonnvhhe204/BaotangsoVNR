import paramiko
import time
from scp import SCPClient
from concurrent.futures import ThreadPoolExecutor

# Danh sách IP thiết bị
devices = [
    "192.168.1.150",
]

USER = "root"
PASSWORD = "cafe@123"
PORT = 22022


def run_remote_script(ip):

    print(f"--- [BẮT ĐẦU] Xử lý máy: {ip} ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, port=PORT, username=USER, password=PASSWORD, timeout=30)

        with open("test_script.sh", "r", encoding="utf-8") as f:
            script_content = f.read()

        extra_cmds = """
        sudo mv /tmp/nginx.conf /etc/nginx/nginx.conf 2>/dev/null
        sudo mv /tmp/app.conf /etc/nginx/conf.d/app.conf 2>/dev/null
        sudo nginx -t && sudo systemctl restart nginx
        """

        stdin, stdout, stderr = ssh.exec_command(
            script_content + extra_cmds, get_pty=True
        )

        for line in iter(stdout.readline, ""):
            clean_line = line.strip()
            # Vẫn in log nhưng có tiền tố IP để phân biệt
            if "https://login.tailscale.com" in clean_line:
                print(f"\n✅ [KẾT QUẢ {ip}]: {clean_line}\n")
                break

    except Exception as e:
        print(f"❌ [LỖI {ip}]: {str(e)}")
    finally:
        ssh.close()
        print(f"--- [XONG] Thiết bị: {ip} ---")


if __name__ == "__main__":
    start_time = time.time()

    # max_workers=7 nghĩa là chạy tối đa 7 máy cùng một thời điểm
    with ThreadPoolExecutor(max_workers=len(devices)) as executor:
        executor.map(run_remote_script, devices)

    end_time = time.time()
    print(
        f"\n Tổng thời gian hoàn thành cho {len(devices)} máy: {end_time - start_time:.2f} giây"
    )
