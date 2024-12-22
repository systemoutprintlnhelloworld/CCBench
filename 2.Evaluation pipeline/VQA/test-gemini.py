from pathlib import Path
import pandas as pd
import google.generativeai as genai
import google.ai.generativelanguage as glm
from tqdm import trange

GOOGLE_API_KEY = ''

genai.configure(api_key=GOOGLE_API_KEY)


def get_image_link(index):
    # ^ open/is题型切换时需要修改
    df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx')

    # get hyperlink value from cell
    # 注意这里的值直接获取是类似'=HYPERLINK("txt/chapter-4/txt/Fig.4.16.txt","Fig.4.16")这种格式,我们需要的是其中的"txt/chapter-4/txt/Fig.4.16.txt"部分
    img_title = df.iloc[index, 3]  # ^ open/is题型切换时需要修改
    # print(f"==>> img_link: {img_title}")
    return img_title


def get_response_from_bard(prompt: str, question: str, image: str):
    model = genai.GenerativeModel('gemini-pro-vision')

    response = model.generate_content(
        glm.Content(
            parts=[
                glm.Part(text=prompt+question),
                glm.Part(
                    inline_data=glm.Blob(
                        mime_type='image/jpeg',
                        data=Path('D:\研究生\任务3\题库\VQA\最终题库\is\img/' +
                                  image).read_bytes()  # ^ open/is题型切换时需要修改
                    )
                ),
            ],
        ),
        stream=False)
    # debug
    # print(response.text)
    # * The prompt_feedback will tell you which safety filter blocked the prompt:
    print('\033[91m' + str(response.prompt_feedback))
    print('\n' + '\033[0m')
    print(response.parts)
    return response.text


# 初始化变量
# ^ open/is题型切换时需要修改
df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx')

if Path('D:\研究生\任务3\测试结果\VQA\is\\bard-test.xlsx').exists():  # ^ open/is题型切换时需要修改
    # ^ open/is题型切换时需要修改
    df_out = pd.read_excel('D:\研究生\任务3\测试结果\VQA\is\\bard-test.xlsx')
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

# 新建一个空的dataframe,用于存储回答,最后保存为excel文档
#! 当回答进度为10/113时(未完成10),start_num=10
start_num = 17
end_num = 181

start_nums = [16, 15]

# 循环读取表格中的图片链接,并调用prompt_image函数

for start_num in start_nums:
    # for start_num in tqdm.tqdm(range(start_num, end_num), unit='条', desc='回答进度'):
    # for start_num in tqdm.tqdm(range(start_num, len(df)), unit='条', desc='回答进度'):
    # 打印当前进度
    print('\n'+'\033[91m'+'start_num: ' + '\033[92m', start_num, '\033[0m')

    # 读取问题
    question = df.iloc[start_num, 0]
    # 在控制台打印蓝色的'问题是'和橙色的question
    print('\033[94m'+'问题是: ' + '\033[93m', question, '\033[0m')
    # 获得图片链接和标题
    img_title = get_image_link(index=start_num)
    # print(f"==>> img_title: {img_title}")
    # 调用prompt_image函数,并将返回值赋值给answer
    answer = get_response_from_bard(
        image=img_title, prompt=prompt, question=question)
    # 将answer转换成json格式
    # 在控制台打印紫色的answer:和黄色的answer
    print('\033[95m'+'答案是:  ' + '\033[93m', answer, '\033[0m')
    # 将question,img_title,answer,reason写入df_out中
    df_out.iloc[start_num, 0] = question
    df_out.iloc[start_num, 1] = img_title
    df_out.iloc[start_num, 2] = answer
    # 将df_out中的内容写入excel
    df_out.to_excel(
        'D:\研究生\任务3\测试结果\VQA\is\\bard-test.xlsx', sheet_name='Sheet1', index=False)  # ^ open/is题型切换时需要修改
