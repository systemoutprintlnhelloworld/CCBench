import replicate
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
client = replicate.Client (
  api_token = ''
)

def get_response_from_llava(image: str, prompt: str, question: str):

		output = client.run(
				'yorickvp/llava-13b:c293ca6d551ce5e74893ab153c61380f5bcbd80e02d49e08c582de184a8f6c83',
				input={
						"image": image,
						"prompt": prompt+question,
				},
		)
		print(type(output))
		return output
		# The yorickvp/llava-13b model can stream output as it's running.
		# The predict method returns an iterator, and you can iterate over that output.
		# for item in output:
		#     # https://replicate.com/yorickvp/llava-13b/api#output-schema
		#     print(item, end="")
  
def tdlm_progress(start_num, total_steps, name="操作"):

    with tqdm.tqdm(total=total_steps, desc=name, unit="条", initial=start_num) as pbar:

        pbar.update(1)
        



# 初始化变量
# ^ open/is题型切换时需要修改
df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx')

# ^ open/is题型切换时需要修改
df_out = pd.read_excel('D:\研究生\任务3\测试结果\VQA\is\\llava.xlsx')

with open('D:\研究生\任务3\提示词/vqa-sys-is-prompt.txt', 'r', encoding='utf-8') as f:  # ^ open/is题型切换时需要修改
    prompt = f.read()

shorten_prompt = '''
Please answer the following questions as an expert in cervical cancer cytology.
'''
#! 当回答进度为10/113时(未完成10),start_num=9
start_num = 130
end_num = 131
for start_num in tqdm.tqdm(range(start_num, end_num), unit='条', desc='回答进度'):
# for start_num in tqdm.tqdm(range(start_num, len(df)), unit='条', desc='回答进度'):
# for start_num in tqdm.tqdm(range(start_num, len(df))):
    # 打印当前进度
    print('\033[91m'+'start_num: ' + '\033[92m', start_num, '\033[0m')

    # 读取问题
    question = df.iloc[start_num, 0]
    print(f"==>> 问题是: {question}")
    # 获得图片链接和标题
    image, img_title = get_image_link(df=df, index=start_num)
    # print(f"==>> img_title: {img_title}")
    # 调用prompt_image函数,并将返回值赋值给answer
    try:
        answer = get_response_from_llava(
            image=image, prompt=prompt, question=question)
    except Exception as e:
        print(f"==>> Error: {e}")
        # 重新回答这一条
        start_num -= 1
        continue
    # 将answer转换成json格式
    print(f"==>>llava answer: {answer}")

    # 将question,img_title,answer,reason写入df_out中
    df_out.iloc[start_num, 0] = question
    df_out.iloc[start_num, 1] = img_title
    df_out.iloc[start_num, 2] = answer
    # 将df_out中的内容写入excel
    df_out.to_excel(
        'D:\研究生\任务3\测试结果\VQA\is\\llava.xlsx', sheet_name='Sheet1', index=False)  # ^ open/is题型切换时需要修改
