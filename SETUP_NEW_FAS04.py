import paramiko
import time
from concurrent.futures import ThreadPoolExecutor

# Thông tin máy điều khiển (Master Node)
MASTER_IP = "192.168.1.250"
USER = "hps"
PASSWORD = "cafe@123"
PORT = 22022

# Danh sách IP các máy con (Worker Nodes)
target_devices = [
    "192.168.1.121",
    "192.168.1.127",
    "192.168.1.114",
    "192.168.1.107",
    "192.168.1.110",
    "192.168.1.131",
    "192.168.1.124",
    "192.168.1.130",
]  # Thêm các IP khác vào đây


def deploy_to_worker(target_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(
            f"--- 🛰️ [CONNECTING] Kết nối tới máy chủ điều khiển {MASTER_IP} để xử lý {target_ip} ---"
        )
        ssh.connect(MASTER_IP, username=USER, password=PASSWORD, timeout=30)

        # Sửa lại biến cmd của bạn như sau:
        ssh_opts = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

        cmd = (
            f"export SSH_OPTS='{ssh_opts}'; "
            f"export GIT_SSH_COMMAND='ssh {ssh_opts}'; "
            f"cd ~/fas04/tools && ./setup_new_fas04.sh {target_ip}"
        )

        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

        for line in iter(stdout.readline, ""):
            print(f"[{target_ip}]: {line.strip()}")

        print(f"✅ [SUCCESS] Hoàn thành {target_ip}")

    except Exception as e:
        print(f"❌ [ERROR {target_ip}]: {str(e)}")
    finally:
        ssh.close()


if __name__ == "__main__":
    start_time = time.time()

    # Chạy song song (ví dụ chạy tối đa 3 máy cùng lúc để tránh treo máy .250)
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(deploy_to_worker, target_devices)

    end_time = time.time()
    print(f"\n🚀 Tổng thời gian thực hiện: {end_time - start_time:.2f} giây")
