'''
本程序目的是1.通过http调用sm.ms图床的api上传图片,
2.生成一个excel文档,记录每个图片在sm.ms图床上上传获得的具体链接
'''

import http
from json import loads
import os
from random import choice
from requests import post
import pandas as pd
import requests

'''
1.通过http调用sm.ms图床的api上传图片

'''

# 读取excel文档中的图片路径


def get_image_file_path(index):
    # get hyperlink value from cell
    # 注意这里的值直接获取是类似'=HYPERLINK("txt/chapter-4/txt/Fig.4.16.txt","Fig.4.16")这种格式,我们需要的是其中的"txt/chapter-4/txt/Fig.4.16.txt"部分
    df = pd.read_excel('D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx')
    img_file_path = df.iloc[index, 3]
    img_title = img_file_path
    # 与'D:\研究生\任务3\题库\VQA\最终题库\open\'拼接成完整的图片路径
    img_file_path = 'D:\研究生\任务3\题库\VQA\最终题库\is\\img\\' + img_file_path
    return img_file_path, img_title


# 上传单个图片到sm.ms并返回图片链接
'''
上传的请求头和参数要求如下

reqtype="fileupload" userhash="####" fileToUpload=(file data here)
'''


def upload_img_to_smms(img_file_path):

    # 定义请求参数
    # 下面折叠的是sm.ms的api调用,但是目前服务器回复400,故暂时不用

    token = ''
    url = 'https://sm.ms/api/v2/upload'
    params = {'format': 'json', 'ssl': True}
    try:
        files = {'smfile': open(img_file_path, 'rb')}
    except FileNotFoundError:
        print("文件不存在")
        return None
    headers = {'Authorization': token}
    if token:
        re = post(url, headers=headers, files=files, params=params)
    else:
        re = post(url, files=files, params=params)

    re_json = loads(re.text)
    print(f"==>> re_json: {re_json}")

    try:
        if re_json['code'] == 'success':
            return re_json['data']['url']
        else:
            return re_json['images']
    except KeyError:
        if re_json['code'] == 'unauthorized':
            raise ConnectionRefusedError
        if re_json['code'] == 'flood':
            raise ConnectionAbortedError

#  https://catbox.moe/user/api.php也支持开发,由于上面那位崩掉了现在只好开发了


UAGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/67.0.3396.87 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
    "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko)"
    "Chrome/6.0.472.63 Safari/534.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like "
    "Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/42.0.2311.135 Safari/537.36",
]


class ImageUploadFailed(Exception):
    pass


def upload_img_to_catbox(img_file_path):
    HEADERS = {
        "User-Agent": choice(UAGENTS),
        "referrer": "https://catbox.moe/",
    }

    with open(img_file_path, 'rb') as f:
        url = 'https://catbox.moe/user/api.php'
        file = {'fileToUpload': f}
        data = {
            'reqtype': 'fileupload',
            'time': '1h',
            'userhash': '',
        }

        # gets link from response
        resp = requests.post(url, headers=HEADERS, data=data, files=file)
        # print(resp.text)
        if resp.status_code == requests.codes.ok:
            try:
                return resp.text
            except ValueError as e:
                raise ImageUploadFailed(
                    f"Failed decoding body:\n{e}\n{resp.content}"
                ) from e
        else:
            raise ImageUploadFailed(
                f"Failed. Status {resp.status_code}:\n{resp.content}"
            )

# 读取excel文档中的图片路径


def get_image_file_path_from_excel(df, excel, index):
    # Add your logic here to get the image file path based on the index
    # For example:
    img_title = df.loc[index, 'img_title']
    img_file_path = os.path.join(excel, img_title)
    return img_file_path, img_title

# 读取某个文件夹下的第i个图片文件路径,不会递归查找子文件夹


def get_image_file_path_from_dir(dir, i):
    # Add your logic here to get the image file path based on the index
    # For example:
    img_title = os.listdir(dir)[i]
    img_file_path = os.path.join(dir, img_title)
    return img_file_path, img_title


'''
2.生成一个excel文档,记录每个图片在sm.ms图床上上传获得的具体链接
'''
# 循环读取excel中所有行的图片名,并拼接为路径打印,测试用
# excel_input = 'D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx'
# excel_output = 'D:\研究生\任务3\题库\VQA\最绂题库\is\is_vqa_web.xlsx'
dir_input = r'D:\研究生\帮师兄评测模型\HQ'
excel_output = r"D:\研究生\帮师兄评测模型\HQ\img_web_url.xlsx"

# df = pd.read_excel(dir_input)

previous_img = ''
count_img = 0
# 创建一个三维df,记录多个子目录下的图片链接,其结构为[[['img_title', 'img_link'],...],...]并将其中第dir个一维df的第一列命名为dir 
df_output = pd.DataFrame(columns=['img_title', 'img_link', 'dir'])
# 遍历dir中所有文件夹,每轮将一个文件夹中的所有图片上传到图床,构建一个双层循环,外层循环遍历文件夹,内层循环遍历文件夹中的图片
for dir in os.listdir(dir_input):
    i=0
    # 判断是否是一个目录
    if not os.path.isdir(os.path.join(dir_input, dir)):
        continue
    print(f"==>> dir: {dir}")
    for i in range(len(os.listdir(os.path.join(dir_input, dir)))):
        # 打印文件中图片总数
        print(f"图片总数: {len(os.listdir(os.path.join(dir_input, dir)))}")


        # img_file_path, img_title = get_image_file_path_from_excel(excel_input, i)
        dir_trails = os.path.join(dir_input, dir)
        img_file_path, img_title = get_image_file_path_from_dir(dir_trails, i)
        # 判断是否是一个图片
        if not img_file_path.endswith('.jpg') and not img_file_path.endswith('.png') and not img_file_path.endswith('.jpeg'):
            print("==>> 不是一个图片,跳过")
            continue
        if previous_img == img_file_path:
            print("==>> 重复图片,跳过")
            continue
        previous_img = img_file_path
        print(f"==>> previous_img: {previous_img}")
        
        response = ""
        response = upload_img_to_smms(img_file_path)
        print(response)
        
        if response == "" or response == None:
            print("第" + str(i) + "张图片在当前文件夹找不到对应文件,跳过")
            continue
        print('\033[92m', "上传成功,链接地址:", response, '\033[0m')
        # 将图片链接写入df_output
        
        df_output = pd.concat([df_output, pd.DataFrame({'img_title': [img_title], 'img_link': [response], 'dir': [dir]})], ignore_index=True)
        
        count_img += 1
        count_img += 1
        print(get_image_file_path_from_dir(dir_trails, i))
        # 写入excel
        df_output.to_excel(excel_output)

# 将df_output写入excel
df_output.to_excel(excel_output)
# ? debug:记录上传图片的数量
print("共上传图片数量:", count_img)
