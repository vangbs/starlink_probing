import os
import subprocess

# 设置文件夹路径
folder_path = 'input'
output_path = 'backbone'

# 确保输出文件夹存在
os.makedirs(output_path, exist_ok=True)

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        input_file = os.path.join(folder_path, filename)
        output_file = os.path.join(output_path, filename.replace('.txt', '.warts'))
        
        # 执行 scamper 命令
        command = [
            "scamper",
            "-p", "10000",
            "-c", "trace -P icmp-paris -q 3 -Q",
            "-f", input_file,
            "-O", "warts",
            "-o", output_file
        ]
        
        print(f"Running scamper for {input_file}, saving to {output_file}")
        subprocess.run(command)

print("Scamper probing completed for matching files.")