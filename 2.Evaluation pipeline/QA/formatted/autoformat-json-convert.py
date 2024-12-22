# 解析excel中json格式字符串,并通过json.load识别,并将识别结果保存在指定excel中

# 本程序旨在实现通过gpt-3.5 识别之前程序无法识别的json格式,并按规定写入excel中具体位置

from openai import OpenAI
import json
import pandas as pd
import os
from tqdm import trange


def json_parser(df_filepath, df_out_filepath):
    # 读取excel中含有json格式字符串的单元格

    df = pd.read_excel(df_filepath)

    # 输出解读json中内容的部分放在指定excel中

    df_out = pd.read_excel(df_out_filepath)

    for num in trange(len(df)):
        # 读取excel中每行第一个单元格内容,如果其中第一个字符为{,则说明是json格式,否则跳过
        current_cell = df.iloc[num, 0]
        print(f"==>> current_cell: {current_cell}")
        if str(current_cell)[0] == '{':
            # 读取json格式字符串
            json_str = current_cell
            # 去除json格式字符串中{前和}后的所有字符
            json_str = json_str[json_str.find('{'):json_str.rfind('}') + 1]
            print(f"==>> json_str: {json_str}")
            # 通过json.load识别json格式
            json_str = json.loads(json_str)
            # 提取json中answer和reason的值
            answer = json_str['answer']
            print(f"==>> answer: {answer}")
            reason = json_str['reason']
            print(f"==>> reason: {reason}")
            df_out.iloc[num, 0] = answer
            df_out.iloc[num, 1] = reason
            # 保存结果
            df_out.to_excel(df_out_filepath, index=False)
        else:
            continue


# 测试
if __name__ == '__main__':
    json_parser(df_filepath='D:\研究生\任务3\测试结果\QA\open\文心一言.xlsx',
                df_out_filepath='D:\研究生\任务3\测试结果\QA\open\文心一言.xlsx')
