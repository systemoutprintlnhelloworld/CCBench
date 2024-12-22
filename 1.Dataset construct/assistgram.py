import os
import sys
import subprocess
import time

def run_program():
    # 这里替换为你的主程序路径
    path_to_program = "ChimeraGPT-vqa.py"

#读取start.txt文件中的数字，作为判断守护程序是否终止的标志
    with  open("D:\研究生\任务3\规划\start.txt", 'r', encoding='utf-8') as file:
        start_num = int(file.read())

    #当start_num为237时，终止守护程序
    while  start_num < 237:
        print("Starting program.")
        try:
            # 使用subprocess运行你的主程序
            subprocess.check_call(["python", path_to_program])
        except subprocess.CalledProcessError:
            print("Program crashed. Restarting...")
            time.sleep(10)  # 可能是api调用超限, 等待10秒后重启程序
        except KeyboardInterrupt:
            print("Program interrupted by user. Exiting...")
            sys.exit()

if __name__ == "__main__":
    run_program()
