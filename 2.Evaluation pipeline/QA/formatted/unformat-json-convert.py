# 本程序旨在实现通过gpt-3.5 识别之前程序无法识别的json格式,并按规定写入excel中具体位置

import time
from openai import OpenAI
import json
import pandas as pd
import os
from tqdm import trange

# openai配置初始化

client = OpenAI(
    # api_key="",
    # base_url="",
    api_key="",
    base_url='',  # & chatanywhere无法使用时解除注释
    # api_key='',  # * adam无法使用时解除注释
    # base_url=''  # * adam无法使用时解除注释
)


def rate_limited(max_per_20_seconds):
    def decorator(func):
        times = []

        def wrapper(*args, **kwargs):
            if len(times) < max_per_20_seconds:
                times.append(time.time())
            else:
                while time.time() - times[0] < 20:
                    time.sleep(0.1)
                times.pop(0)
                times.append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator

# @rate_limited(1)  # 10秒内最多调用1次


def get_response(json_str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                        "content": '''
                请把下面的异常json格式字符串转换为正常格式,你只需要把整理好的json格式字符串,其他都不要回答
                如
                用户'{  "reason": "A',  'answer': 'B'}'
                回答:'
                {"reason": "A","answer": "B"}
                '''
            },
            {
                "role": "user",
                        "content": json_str
            }
        ],
    )
    return response


def json_parser(df_filepath, df_out_filepath):
    # 读取excel中含有json格式字符串的单元格

    df = pd.read_excel(df_filepath)

    # 输出解读json中内容的部分放在指定excel中

    df_out = pd.read_excel(df_out_filepath)

    num = 188  # ! 此处可以修改

    for num in trange(num, len(df)):
        # 读取excel中每行第一个单元格内容,如果其中第一个字符为{,则说明是json格式,否则跳过
        current_cell = df.iloc[num, 0]
        print(f"==>> current_cell: {current_cell}")
        if str(current_cell)[0] == '{':
            # 读取json格式字符串
            json_str = current_cell
            # 调用gpt-3.5 识别json格式
            response = get_response(json_str)
            # 用json.load识别json格式
            response = response.choices[0].message.content
            # 剔除回复中{前的字符和}后的字符
            response = response[response.find('{'):response.rfind('}')+1]
            print(f"==>> GPT3.5 response: {response}")
            response = json.loads(response)
            # 其中键为answer和reason,分别保存其值
            answer = response["answer"]
            print(f"==>> answer: {answer}")
            reason = response["reason"]
            print(f"==>> reason: {reason}")
            df_out.iloc[num, 0] = answer
            df_out.iloc[num, 1] = reason
            # 保存结果
            df_out.to_excel(df_out_filepath, index=False)
        else:
            print("无需整理")


# 测试
if __name__ == '__main__':
    json_parser(df_filepath='D:\研究生\任务3\测试结果\QA\open\文心一言.xlsx',
                df_out_filepath='D:\研究生\任务3\测试结果\QA\open\文心一言.xlsx')
