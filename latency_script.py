import os
import subprocess

# 定义输入文件夹路径
input_folder = "input"
with open('island_countries.txt', 'r') as file:
    regions = [line.strip() for line in file]

def main():
    # 遍历所有文件
    for file_name in os.listdir(input_folder):
        name = file_name.replace('.txt','')
        if name not in regions:
            continue
        command = [
            'python3',
            'latency_trace_sim.py',
            name,
            '75',
            '3',
            '10800'
        ]
        subprocess.run(command)

if __name__ == "__main__":
    main()
