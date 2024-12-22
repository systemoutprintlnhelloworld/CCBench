import multiprocessing
import pandas as pd
import openpyxl
import openai
from openpyxl.styles import PatternFill

def revise_gpt_auto():
    # 读取数据
    df = pd.read_excel("D:\\研究生\\任务3\\题库\\VQA\\VQA题库(new)_modified.xlsx")


    openai.api_base = ''
    openai.api_key = ""


    df_new = df


    # 定义填充颜色
    fill = PatternFill(fill_type="solid", start_color="FF8000")

    # 从第一列的252行开始读取
    for i in range(255, len(df)):
        text = df.iloc[i, 0]

        system_prompt = "你是一位细胞病理学专家，目前正在处理的是宫颈癌细胞病理学图像，目前需要对题库中的题目进行筛查，当输入文本在陈述一些没有特指图像中细胞的，孤立的细胞学常识而不是在根据图像描述细胞的形态等，则打印\"结果:No|原因:[你给出的理由]\"，如果出现 in this image/for this image,insert等明显说明是对具体图像进行描述的，则跳过该行，打印:\"结果:Yes\""

        # GPT-4模型
        result = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text},
        ]

        
    )
        # debug
        print(result['choices'][0]['message']['content'])
        # 打印此时进度,并输出一个进度条
        print("现在是 第" + str(i+1) + "行")
        print("进度: {}/{}".format(i, len(df)))

        if result == 'Yes' or result == 'yes':
            # 跳过该行
            continue
        elif "|" in result:
            result, reason = result.split("|", 1)
            df_new.loc[i, 1] = result
            # 如果结果是'No'或者'no'
            if result == 'No' or result == 'no':
                # 将该单元格背景变为橙色
                df_new.iloc[i, 1].fill = fill
            df_new.loc[i, 2] = reason
        else:
            i -= 1 # 上一条结果无效，需重新计算


    writer = pd.ExcelWriter("D:\\研究生\\任务3\\题库\\VQA\\VQA题库(new)_modified.xlsx", engine='openpyxl')
    df_new.to_excel(writer, index=False)

    writer.save()
    print("完成")   

# 使用multiprocessing.Process创建子进程
if __name__ == '__main__':
    import time
    import sys
    import os
    import atexit
    import signal

    p = multiprocessing.Process(target=revise_gpt_auto)
    p.start()

    def sigterm_handler(signo, frame):
        sys.exit(1)

    signal.signal(signal.SIGTERM, sigterm_handler)

    def exit_handler():
        p.terminate()

    atexit.register(exit_handler)
    p.join()
    print("子进程已结束，主进程也结束")
        

