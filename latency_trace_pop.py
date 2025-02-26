import random
import sys
import time
import subprocess
import os
import shutil


def run_for_pinging(input_file, output_dir, iteration):
    """对 input.txt 里的 IP 进行 fping 探测，并返回可达 IP 列表"""
    output_file = os.path.join(output_dir, "output.txt")

    # 使用 fping 进行 ping 探测
    command = [
        "fping",
        "-c", "1",
        "-f", input_file,
        "-q",
    ]

    with open(output_file, "w") as file:
        subprocess.run(command, stdout=file, stderr=subprocess.STDOUT)

    reachable_ips = []
    latency = []

    with open(output_file, "r") as file:
        for line in file:
            if "min/avg/max" not in line:
                latency.append('*')
                continue
            stats = line.split("min/avg/max = ")[-1].strip()
            latency.append(stats.split('/')[0])
            ip = line.split(" : xmt")[0].strip()
            reachable_ips.append(ip)
    
    
    with open(os.path.join(output_dir, f"ping_{iteration}.txt"), "w") as file:
        for _ in latency:
            file.write(f"{_}\n")

    return reachable_ips


def main(input_name, sample_size, time_step, time_horizon):
    input_file = f'input/{input_name}.txt'
    output_dir = f"ping_output/{input_name}"
    
    # 清空输出目录
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # 读取所有 IP
    with open(input_file, "r") as file:
        all_ips = [line.strip() for line in file if line.strip()]

    # 需要优先选择的 IP 列表
    forced_ips = [
        "203.98.224.11",
    ] 

    reachable_ips = run_for_pinging(input_file, output_dir, 0)
    print(f"Initial scan found {len(reachable_ips)} reachable IPs.")

    # **确保 forced_ips 里的 IP 在可达列表中**
    selected_ips = [ip for ip in forced_ips if ip in reachable_ips]

    # 计算还需要多少个 IP
    remaining_needed = sample_size - len(selected_ips)

    if remaining_needed > 0:
        # 从 reachable_ips 中随机选取不在 forced_ips 里的 IP
        other_candidates = [ip for ip in reachable_ips if ip not in selected_ips]
        selected_ips += random.sample(other_candidates, min(remaining_needed, len(other_candidates)))

    # **保存初始选择的 IP**
    initial_selected_file = os.path.join(output_dir, "input.txt")
    with open(initial_selected_file, "w") as file:
        for ip in selected_ips:
            file.write(f"{ip}\n")

    # **周期性探测阶段**
    end_time = time.time() + time_horizon
    iteration = 0

    while time.time() < end_time:
        start_time = time.time()

        run_for_pinging(initial_selected_file, output_dir, iteration)

        elapsed_time = time.time() - start_time
        print(elapsed_time)

        if elapsed_time < time_step:
            time.sleep(time_step - elapsed_time)

        iteration += 1


if __name__ == "__main__":
    input_name = sys.argv[1]
    sample_size = int(sys.argv[2])  # 采样数量
    time_step = float(sys.argv[3])  # 时间步长（秒）
    time_horizon = float(sys.argv[4])  # 时间范围（秒）
    main(input_name, sample_size, time_step, time_horizon)

#python3 latency_trace_pop.py "sydyaus1_NR-14_Yaren" 150 3 86400