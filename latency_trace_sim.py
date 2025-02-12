import random
import sys
import time
import subprocess
import os
import shutil
import json

offset = 2

def process_with_scamper(input_file, output_file):
    """使用 Scamper 对所有 IP 进行处理并生成 warts 文件"""
    start = time.time()
    command = [
        "scamper",
        "-p", "5000",
        "-c", "trace -P icmp-paris -q 3 -Q",
        "-f", input_file,
        "-O", "warts",
        "-o", output_file
    ]
    subprocess.run(command)


def parse_warts_to_json(warts_file, json_file):
    command = ["sc_warts2json", warts_file]
    with open(json_file, "w") as output_file:
        subprocess.run(command, stdout=output_file)


def extract(trace_data):
    if 'hops' not in trace_data:
        return None
    hops = trace_data['hops']
    if not hops:
        return None

    # 对每一跳的探测结果进行排序，按 probe_id 排序
    sorted_hops = sorted(hops, key=lambda x: x['probe_id'])
    dst_ip = trace_data['dst']

    for hop in sorted_hops:
        if hop['addr'].startswith("2620:134:b0ff") or hop['addr'].startswith("2620:134:b004"):
            # 查找当前跳的下一跳
            for next_hop in sorted_hops:
                if (next_hop['probe_id'] == hop['probe_id'] and 
                    next_hop['probe_ttl'] == hop['probe_ttl'] + offset and 
                    next_hop['addr'] == dst_ip):
                    return hop['addr'], dst_ip

    return None


def extract_last_two_hops(json_file):
    """从 JSON 文件中提取最后两跳的 IP"""
    last_two_hops = []
    with open(json_file, 'r') as file:
        for line in file:
            trace_data = json.loads(line)
            if trace_data['type'] == 'trace':
                result = extract(trace_data)
                if result:
                    last_two_hops.append(result)

    return last_two_hops


def run_for_pinging(input_file, output_dir, iteration):
    output_file = os.path.join(output_dir, "output.txt")

    # fping -c 1 -f input.txt -q
    command = [
        "fping",
        "-c", "1",
        "-f", input_file,
        "-q",
    ]

    with open(output_file, "w") as file:
        subprocess.run(command, stdout=file, stderr=subprocess.STDOUT)
    
    latency = []

    with open(output_file, "r") as file:
        for line in file:
            if "min/avg/max" not in line:
                latency.append('*')
                continue
            stats = line.split("min/avg/max = ")[-1].strip()
            latency.append(stats.split('/')[0])

    with open(os.path.join(output_dir, f"ping_{iteration}.txt"), "w") as file:
        for _ in latency:
            file.write(f"{_}\n")


def main(input_name, sample_size, time_step, time_horizon):
    input_file = f'input/{input_name}.txt'
    output_dir = f"ping_output/{input_name}"
    warts_file = os.path.join(output_dir, f"{input_name}.warts")
    json_file = os.path.join(output_dir, f"{input_name}.json")
    
    # 清空输出目录
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # 使用 Scamper 生成 warts 文件
    process_with_scamper(input_file, warts_file)

    # 将 warts 转换为 JSON
    parse_warts_to_json(warts_file, json_file)

    # 提取最后两跳的 IP
    last_two_hops = extract_last_two_hops(json_file)

    # 保存结果到文件
    last_two_hops_file = os.path.join(output_dir, "last_two_hops.txt")
    with open(last_two_hops_file, 'w') as file:
        for second_last, last in last_two_hops:
            file.write(f"{second_last} {last}\n")

    # 从 last_two_hops 中随机选取 sample_size 对
    if len(last_two_hops) < sample_size:
        selected_pairs = last_two_hops
    else:
        selected_pairs = random.sample(last_two_hops, sample_size)

    # 每 time_step 对所有 IP 使用 Scamper 进行一次 ping
    end_time = time.time() + time_horizon
    iteration = 0
    ip_list = [ip for pair in selected_pairs for ip in pair]
    input_file = os.path.join(output_dir, "input.txt")
    with open(input_file, "w") as file:
        for ip in ip_list:
            file.write(f"{ip}\n")
    
    while time.time() < end_time:
        start_time = time.time()
        run_for_pinging(input_file, output_dir, iteration)
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

#python3 latency_trace_sim.py "sydyaus1_TO-04_Nuku'alofa" 75 3 1800
#python3 latency_trace_sim.py "acklnzl1_TO-04_Nuku'alofa" 75 3 1800
#python3 latency_trace_sim.py "frntdeu1_YT-YT_Mayotte" 75 3 86400
#python3 latency_trace_sim.py "sydyaus1_NR-14_Yaren" 75 3 86400