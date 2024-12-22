import os
import replicate
import pandas as pd
import tqdm
from http import HTTPStatus
import dashscope
from gradio_client import Client

# 注:测试模型为lucataco/qwen-vl-chat


def get_image_url(df, index):
    # get hyperlink value from cell
    # 注意这里的值直接获取是类似'=HYPERLINK("txt/chapter-4/txt/Fig.4.16.txt","Fig.4.16")这种格式,我们需要的是其中的"txt/chapter-4/txt/Fig.4.16.txt"部分
    img_title = df.iloc[index, 2]  # ^ open/is题型切换时需要修改
    # 通过img_title在当前文件夹下另一个excel'open_vqa_web'中找到同样名字的单元格,获取该单元格的行数,并获取当前行的第二列的值,即图片的链接
    df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa_web.xlsx')
    line_number = df[df['img_title'] == img_title].index.tolist()[0]
    img_link = df.iloc[line_number, 2]
    # print(f"==>> img_link: {img_link}")
    return img_link, img_title


def get_image_path(df, index):
    img_title = df.iloc[index, 3]
    print(f"==>> img_title: {img_title}")
    # 在当前文件夹的img文件夹下寻找同样名字的图片,返回其本地路径
    img_path = f"D:\研究生\任务3\题库\VQA\最终题库\is\img/{img_title}"
    print(f"==>> img_path: {img_path}")
    return img_path, img_title


# replicate-style
# os.environ["DASHSCOPE_API_KEY"] = ''
# aliyun-style
dashscope.api_key = ''

# ? 阿里云


def get_response_from_qwen_aliyun(image: str, prompt: str, question: str):
    """Simple single round multimodal conversation call.
    """

    messages = [
        {
            "role": "system",
            "content": [
                {"text": prompt}
            ],
            "role": "user",
            "content": [
                {"image": image},
                {"text": question}
            ]
        }
    ]
    response = dashscope.MultiModalConversation.call(model="qwen-vl-max",
                                                     messages=messages)
    # The response status_code is HTTPStatus.OK indicate success,
    # otherwise indicate request is failed, you can get error code
    # and message from code and message.
    if response.status_code == HTTPStatus.OK:
        '''{"status_code": 200, "request_id": "", "code": "", "message": "", "output": {"text": null, "finish_reason": null, "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": [{"text": "The nucleus of the metaplastic cell has an oval or round shape, which is typical for most cells."}]}}]}, "usage": {"input_tokens": 1266, "output_tokens": 23, "image_tokens": 1218}}'''
        # 如何从其中提取text中的内容,上面这种方式报错Error: 'dict' object has no attribute 'text'
        print(response)
        # print(response.output.choices[0].message.content)
        print(response.output.choices[0].message.content[0]['text'])
        # Fix: Access the 'text' attribute correctly
        return response.output.choices[0].message.content[0]['text']
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.
        print(response.status_code)  # The status code.


# ? replicate


def get_response_from_qwen_replicate(image: str, prompt: str, question: str):

    output = replicate.run(
        ref="lucataco/qwen-vl-chat:50881b153b4d5f72b3db697e2bbad23bb1277ab741c5b52d80cd6ee17ea660e9",
        input={
            "image": image,  # local file path
            "prompt": prompt+question,
        }
    )
    print(output.encode('utf-8').decode('utf-8'))

    print(type(output))
    return output
    # The yorickvp/llava-13b model can stream output as it's running.
    # The predict method returns an iterator, and you can iterate over that output.
    # for item in output:
    #     # https://replicate.com/yorickvp/llava-13b/api#output-schema
    #     print(item, end="")

# HF


def get_response_from_qwen_hf(image: str, prompt: str, question: str):
    # 将img中的所有\替换为/,并在前面加上file:///
    image = "file=\\" + image.replace("\\", "/")
    print("file_path:", image)
    client = Client(
        "https://modelscope.cn/api/v1/studio/qwen/Qwen-VL-Chat-Demo/gradio/")
    result = client.predict(
        # str (filepath to JSON file) in 'Qwen-VL-Max' Chatbot component
        "https://modelscope.cn/api/v1/studio/qwen/Qwen-VL-Chat-Demo/gradio/file=/tmp/gradio/6c3db31bc040eae20aedacc634a89e0328195035/Fig.1.17.jpg",
        "Howdy!",  # str  in 'Input' Textbox component
        fn_index=0
    )
    print(result := result.output.choices[0].message.content.text)
    return result


def tdlm_progress(start_num, total_steps, name="操作"):

    with tqdm.tqdm(total=total_steps, desc=name, unit="条", initial=start_num) as pbar:

        pbar.update(1)


# 初始化变量
# ^ open/is题型切换时需要修改
df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx')

# ^ open/is题型切换时需要修改
df_out = pd.read_excel('D:\研究生\任务3\测试结果\VQA\is\\qwen-vl-max.xlsx')

with open('D:\研究生\任务3\提示词/vqa-sys-is-prompt.txt', 'r', encoding='utf-8') as f:  # ^ open/is题型切换时需要修改
    prompt = f.read()

shorten_prompt = '''
Please answer the following questions as an expert in cervical cancer cytology.
'''
#! 当回答进度为10/113时(未完成10),start_num=9
start_num = 67  # plus 10 未测试

for start_num in tqdm.tqdm(range(start_num, len(df)), unit='条', desc='回答进度'):
    # for start_num in tqdm.tqdm(range(start_num, len(df)), unit='条', desc='回答进度'):
    # for start_num in tqdm.tqdm(range(start_num, len(df))):
    # 打印当前进度
    print('\033[91m'+'start_num: ' + '\033[92m', start_num, '\033[0m')

    # 读取问题
    question = df.iloc[start_num, 0]
    print(f"==>> 问题是: {question}")
    # 获得图片链接和标题
    # image, img_title = get_image_url(df=df, index=start_num)
    image, img_title = get_image_path(df=df, index=start_num)
    image = 'file://' + image.replace('\\', '/')
    print(f"==>> img: {image}")
    # print(f"==>> img_title: {img_title}")
    # 调用prompt_image函数,并将返回值赋值给answer
    try:
        answer = get_response_from_qwen_aliyun(
            image=image, prompt=prompt, question=question)
    except Exception as e:
        print(f"==>> Error: {e}")
        break
        # 重新回答这一条
        start_num -= 1

        continue
    # 将answer转换成json格式
    print(f"==>>qwen answer: {answer}")

    # 将question,img_title,answer,reason写入df_out中
    df_out.iloc[start_num, 0] = question
    df_out.iloc[start_num, 1] = img_title
    df_out.iloc[start_num, 2] = answer
    # 将df_out中的内容写入excel
    df_out.to_excel(
        'D:\研究生\任务3\测试结果\VQA\is\\qwen-vl-max.xlsx', sheet_name='Sheet1', index=False)  # ^ open/is题型切换时需要修改
