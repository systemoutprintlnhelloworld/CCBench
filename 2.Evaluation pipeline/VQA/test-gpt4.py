
import base64
from pathlib import Path
import pandas as pd
import numpy as np
import http.client
import json
from tqdm import tqdm
from openai import OpenAI
# OpenAI API Key
# api_base = ""
# api_key = ""

api_base = ''
api_key = ''

client = OpenAI(
    # & chatanywhere无法使用时解除注释
    # api_key="",
    # base_url='https://api.adamchatbot.chat/v1/'  # & chatanywhere无法使用时解除注释
    api_key='',  # * adam无法使用时解除注释
    base_url='https://api.chatanywhere.cn/v1'  # * adam无法使用时解除注释
    # api_key="",  # ~ 以上两种均无法使用时解除注释
    # base_url="https://api.rikka.love/v1/"  # ~ 以上两种均无法使用时解除注释
)

# Function to get image link from excel


def get_image_link(df, index):
    # get hyperlink value from cell
    # 注意这里的值直接获取是类似'=HYPERLINK("txt/chapter-4/txt/Fig.4.16.txt","Fig.4.16")这种格式,我们需要的是其中的"txt/chapter-4/txt/Fig.4.16.txt"部分
    img_title = df.iloc[index, 3]  # ^ open/is题型切换时需要修改
    # 通过img_title在当前文件夹下另一个excel'open_vqa_web'中找到同样名字的单元格,获取该单元格的行数,并获取当前行的第二列的值,即图片的链接
    df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa_web.xlsx')
    line_number = df[df['img_title'] == img_title].index.tolist()[0]
    img_link = df.iloc[line_number, 2]
    print(f"==>> img_link: {img_link}")
    return img_link, img_title


def compose_headers(api_key: str) -> dict:
    return {\
        "Content-Type": "application/json",
        'Accept': 'application/json',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        "Authorization": api_key
    }


def compose_payload(image: str, prompt: str, question: str) -> dict:
    payload = json.dumps({
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": image+question+prompt
            }
        ]
    })
    return payload


def get_response_from_openai(image: str, prompt: str, question: str):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content":
                        [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url":
                                {
                                    "url": image,
                                },
                            },
                        ],
            }
        ],
        max_tokens=300,
    )
    return response


def prompt_image(api_key: str, image: str, prompt: str, question: str) -> str:
    conn = http.client.HTTPSConnection("api.rikka.love")
    headers = compose_headers(api_key=api_key)
    payload = compose_payload(image=image, prompt=prompt, question=question)
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def tdlm_progress(start_num, total_steps, name="操作"):

    with tqdm(total=total_steps, desc=name, unit="条", initial=start_num) as pbar:

        pbar.update(1)


# 初始化变量
# ^ open/is题型切换时需要修改
df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx')
# 备份df,另存为open_vqa_backup.xlsx
df.to_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa_backup.xlsx',
            index=False)  # ^ open/is题型切换时需要修改

if Path('D:\研究生\任务3\测试结果\VQA\is\\gpt-4.xlsx').exists():  # ^ open/is题型切换时需要修改
    # ^ open/is题型切换时需要修改
    # ^ open/is题型切换时需要修改
    df_out = pd.read_excel('D:\研究生\任务3\测试结果\VQA\is\\gpt-4.xlsx')
else:
    # ^ open/is题型切换时需要修改
    df_out = pd.DataFrame(columns=['question', 'image_title', 'answer'])

with open('D:\研究生\任务3\提示词/vqa-sys-is-prompt.txt', 'r', encoding='utf-8') as f:  # ^ open/is题型切换时需要修改
    prompt = f.read()

example_question = '''
Q: What is the nucleoplasmic ratio of the cells shown in this picture? example.jpg(in the real case it is a picture you can see,but it is an example here)
'''  # ^ open/is题型切换时需要修改

example_answer = '''
{
"reason":"Based on the information in the picture, the cytoplasm is very close to the nucleus",
"answer":"close to 1"
}
'''  # ^ open/is题型切换时需要修改

#! 当回答进度为10/113时(未完成10),start_num=9
start_num = 103

start_nums = [14,261,262,263,273,274]

# 循环读取表格中的图片链接,并调用prompt_image函数
# for start_num in range(start_num, end_num):
for start_num in start_nums:
    # for start_num in range(start_num, len(df)):
    # 打印当前进度
    print('\033[91m'+'start_num: ' + '\033[92m', start_num, '\033[0m')
    

    # 更新并打印进度条
    tdlm_progress(start_num, len(df), name="回答进度")
    # 读取问题
    question = df.iloc[start_num, 0]
    print(f"==>> 问题是: {question}")
    # 获得图片链接和标题
    image, img_title = get_image_link(df=df, index=start_num)
    # print(f"==>> img_title: {img_title}")
    # 调用prompt_image函数,并将返回值赋值给answer
    answer = get_response_from_openai(
        image=image, prompt=prompt, question=question)
    # 将answer转换成json格式
    print(f"==>>GPT-4 answer: {answer}")
    answer = answer.choices[0].message.content

    # 将question,img_title,answer,reason写入df_out中
    df_out.iloc[start_num, 0] = question
    df_out.iloc[start_num, 1] = img_title
    df_out.iloc[start_num, 2] = answer
    # 将df_out中的内容写入excel
    df_out.to_excel(
        'D:\研究生\任务3\测试结果\VQA\is\gpt-4.xlsx', sheet_name='Sheet1', index=False)  # ^ open/is题型切换时需要修改
