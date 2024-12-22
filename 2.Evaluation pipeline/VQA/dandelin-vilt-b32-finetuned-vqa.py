from gradio_client import Client
import pandas as pd
import tqdm


def get_image_link(df, index):
    # get hyperlink value from cell
    # 注意这里的值直接获取是类似'=HYPERLINK("txt/chapter-4/txt/Fig.4.16.txt","Fig.4.16")这种格式,我们需要的是其中的"txt/chapter-4/txt/Fig.4.16.txt"部分
    img_title = df.iloc[index, 3]  # ^ open/is题型切换时需要修改
    # 通过img_title在当前文件夹下另一个excel'open_vqa_web'中找到同样名字的单元格,获取该单元格的行数,并获取当前行的第二列的值,即图片的链接
    df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa_web.xlsx')
    line_number = df[df['img_title'] == img_title].index.tolist()[0]
    img_link = df.iloc[line_number, 2]
    # print(f"==>> img_link: {img_link}")
    return img_link, img_title


def get_response_from_vilt(image: str, prompt: str, question: str):
    client = Client(
        'https://ni-cai-dandelin-vilt-b32-finetuned-vqa-my-config.hf.space/--replicas/rsu55/')
    result = client.predict(
        # filepath  in 'Input Image' Image component
        image,
        question,  # str  in 'Question' Textbox component
        api_name="/predict"
    )
    print(result)
    return result['label']


def tdlm_progress(start_num, total_steps, name="操作"):

    with tqdm.tqdm(total=total_steps, desc=name, unit="条", initial=start_num) as pbar:

        pbar.update(1)


# 初始化变量
# ^ open/is题型切换时需要修改
df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx')

# ^ open/is题型切换时需要修改
df_out = pd.read_excel('D:\研究生\任务3\测试结果\VQA\is\\vilt.xlsx')

with open('D:\研究生\任务3\提示词/vqa-sys-is-prompt.txt', 'r', encoding='utf-8') as f:  # ^ open/is题型切换时需要修改
    prompt = f.read()

shorten_prompt = '''
Please answer the following questions as an expert in cervical cancer cytology.
'''
#! 当回答进度为10/113时(未完成10),start_num=9
start_num = 113
end_num = 122

start_nums = [89, 98, 104, 105, 108, 123, 127, 129, 135,
              136, 182, 185, 233, 248, 261, 287, 288, 289, 294, 295]
for start_num in start_nums:
    # for start_num in range(start_num,end_num):
    # for start_num in range(start_num, len(df)):
    # 打印当前进度
    print('\033[91m'+'start_num: ' + '\033[92m', start_num, '\033[0m')

    # 更新并打印进度条
    tdlm_progress(start_num, len(df), name="回答进度")
    # 读取问题
    question = df.iloc[start_num, 0]
    # 截取question中的前40个字符,避免输入过长
    question = question[:40]
    print(f"==>> 问题是: {question}")
    # 获得图片链接和标题
    image, img_title = get_image_link(df=df, index=start_num)
    # print(f"==>> img_title: {img_title}")
    # 调用prompt_image函数,并将返回值赋值给answer
    try:
        answer = get_response_from_vilt(
            image=image, prompt=shorten_prompt, question=question)
    except Exception as e:
        print(f"==>> Error: {e}")
        # 重新回答这一条
        start_num -= 1
        continue
    # 将answer转换成json格式
    print(f"==>>Vilt answer: {answer}")

    # 将question,img_title,answer,reason写入df_out中
    df_out.iloc[start_num, 0] = question
    df_out.iloc[start_num, 1] = img_title
    df_out.iloc[start_num, 2] = answer
    # 将df_out中的内容写入excel
    df_out.to_excel(
        'D:\研究生\任务3\测试结果\VQA\is\\vilt.xlsx', sheet_name='Sheet1', index=False)  # ^ open/is题型切换时需要修改
