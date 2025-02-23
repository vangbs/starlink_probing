import os
import json
import ipaddress
import sys
from collections import defaultdict, Counter

# 设置文件夹路径
input_path = 'input'
output_path = 'backbone'
json_path = 'backbone_json'
pop_output_path = f'backbone_pop_{sys.argv[1]}'

# 定义一个函数来读取多行JSON数据
def read_json_lines(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)


def extract(trace_data):
    if 'hops' not in trace_data:
        return None
    hops = trace_data['hops']
    if not hops:
        return None

    sorted_hops = sorted(hops, key=lambda x: x['probe_id'])
    last_matching_hop = None

    first_target_prefix = "2620:134:b0ff:"
    second_target_prefix = "2620:134:b0fe:"

    ttl_groups = defaultdict(list)
    for hop in sorted_hops:
        ttl_groups[hop['probe_ttl']].append(hop)

    for ttl, hops_at_ttl in ttl_groups.items():
        ip_counts = Counter(hop['addr'] for hop in hops_at_ttl)
        valid_ips = {ip for ip, count in ip_counts.items() if count >= 3}
        curr_delay = min(hop['rtt'] for hop in hops_at_ttl)

        for hop in hops_at_ttl:
            if hop['addr'] in valid_ips and hop['addr'].startswith(first_target_prefix):
                for next_hop in sorted_hops:
                    if (next_hop['probe_id'] == hop['probe_id'] and 
                        next_hop['probe_ttl'] == hop['probe_ttl'] + 1 and 
                        next_hop['addr'].startswith(second_target_prefix)):
                        last_matching_hop = hop
                        break

                    if (next_hop['probe_id'] == hop['probe_id'] and 
                        next_hop['probe_ttl'] - hop['probe_ttl'] == 1 and 
                        next_hop['addr'] == trace_data['dst']):
                        last_matching_hop = hop
                        break
    if last_matching_hop and last_matching_hop['addr'] == '2620:134:b0ff::70':
        print(trace_data['dst'])
    if last_matching_hop:
        return last_matching_hop
    '''
    for ttl, hops_at_ttl in ttl_groups.items():
        ip_counts = Counter(hop['addr'] for hop in hops_at_ttl)
        valid_ips = {ip for ip, count in ip_counts.items() if count >= 3}
        curr_delay = min(hop['rtt'] for hop in hops_at_ttl)

        for hop in hops_at_ttl:
            if hop['addr'] in valid_ips and hop['addr'].startswith(first_target_prefix):
                for next_hop in sorted_hops:
                    if (next_hop['probe_id'] == hop['probe_id'] and 
                        next_hop['probe_ttl'] - hop['probe_ttl'] == 2 and 
                        next_hop['addr'] == trace_data['dst']):
                        last_matching_hop = hop
                        break
    '''
    return last_matching_hop

'''
pops = [
    "acklnzl1", "mnlaphl1", "sydyaus1", "ashnvax2", "atlagax1", "bgtacol1", "bnssarg1", "chcoilx1",
    "dllstxx1", "frtabra1", "limaper1", "mmmiflx1", "mplsmnx1", "nwyynyx1", "qrtomex1", 'dohaqat1',
    "sntochl1", "splobra1", "dnvrcox1", "lsancax1", "sltyutx1", "snjecax1", "sttlwax1", 'sfiabgr1',
    "tmpeazx1", "frntdeu1", "lgosnga1", "lndngbr1", "mdrdesp1", "prthaus1", "sngesgp1", "tkyojpn1",
    'jtnaidn1'
]
'''

pops = [
    'clgycan1', 'mlnnita1', 'wrswpol1','dohaqat1'
]
def islegal(filename):
    for a in pops:
        if a in filename:
            return True
    return False

# 创建输出目录
os.makedirs(pop_output_path, exist_ok=True)

# 初始化每个 POP 的 IP 列表
pop_results = {pop: set() for pop in pops}

# 遍历输入文件夹
for filename in os.listdir(input_path):
    if filename.endswith('.txt') and islegal(filename):
        name = filename.replace('.txt', '')
        warts_file = f"{output_path}/{name}.warts"
        json_file = f"{json_path}/{name}.json"

        # 检查对应的 .warts 文件是否存在
        if os.path.isfile(warts_file):
            # 生成 JSON 文件
            cmd = f'sc_warts2json "{warts_file}" > "{json_file}"'
            os.system(cmd)
            print(f"Generated JSON: {json_file}")

            # 处理 JSON 文件
            for item in read_json_lines(json_file):
                if item['type'] == 'trace':
                    result = extract(item)
                    if result:
                        for pop in pops:
                            if pop in filename:  # 判断文件名是否包含 POP
                                pop_results[pop].add(result['addr'])

            # 删除 JSON 文件
            os.remove(json_file)
            print(f"Deleted JSON: {json_file}")

# 写入每个 POP 的结果到单独的文件
total = 0
for pop, ip_set in pop_results.items():
    unique_ips = sorted(ip_set)
    total += len(unique_ips)
    with open(f"{pop_output_path}/{pop}.txt", 'w') as file:
        for ip in unique_ips:
            file.write(f"{ip}\n")
    print(f"Processed POP: {pop}, IPs: {len(unique_ips)}")

print(f"Total unique IPs processed: {total}")
