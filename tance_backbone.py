import os
import sys
from multiprocessing import Process
import subprocess
import shutil

folder_path = 'backbone_pop'
output_path = 'backbone_trace_' + sys.argv[1]

file_ips = {}

for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        with open(os.path.join(folder_path, filename), 'r') as file:
            ips = [line.strip() for line in file]
            file_ips[filename.replace('.txt', '')] = ips

def run_mtr(ip, output_file):
    with open(output_file, 'a') as f:
        subprocess.run(["mtr", "-r", "-i", "1", "-c", "50", "-n", ip], stdout=f)

def trace_mtr(filename, ips):
    for ip in ips:
        run_mtr(ip, filename)
    print(f'{filename} completed.')

if os.path.exists(output_path):
    shutil.rmtree(output_path)
os.makedirs(output_path)

# 为每个文件启动一个独立的进程
for filename, ips in file_ips.items():
    output_file = os.path.join(output_path, filename + '.txt')
    p = Process(target=trace_mtr, args=(output_file, ips))
    p.start()
