""" 本程序通过多种方式读取图片文件，然后将图片上传到 sm.ms 图床，接着使用 OpenAI 的 GPT-4 模型分析图片内容。
"""
import base64
from json import loads, dump
import json
import os
from httpx import post, get
from openai import OpenAI
import time
from tqdm import tqdm  # 导入 tqdm 用于显示进度条

# todo 
# 1.进度条 
# 2.断点续传
# 3.异常处理方案详细化
# 4.程序异常&正常执行通知推送
# 5.程序异常日志

# 第三方 API 客户端初始化
client = OpenAI(
    base_url='https://noapi.ggb.today/v1/',
    api_key=''
)

def main():
    # 图片目录路径
    dir_path = r"D:\研究生\帮师兄评测模型\师兄的会议\CD_512"
    # JSON 文件中要处理的文件名
    json_file = r'D:\研究生\帮师兄评测模型\师兄的会议\untest.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        image_list = json.load(f)
    
    # 遍历JSON中的所有图片并调用 API
    loop_call_api(dir_path, image_list)


# 遍历JSON中的所有图片，调用 API 进行处理，如果需要则最多重试 5 次
# 并将结果记录到 JSON 文件中
def loop_call_api(dir_path, image_list):
    # 结果存储文件
    results_file = r'D:\研究生\帮师兄评测模型\师兄的会议\results_add.json'
    results = []
    
    # 使用 tqdm 创建进度条
    with tqdm(total=len(image_list), desc="处理进度", unit="张图片") as pbar:
        # 处理 JSON 文件中指定的文件
        for file in image_list:
            image_path = os.path.join(dir_path, file)
            retry_count = 0
            max_retries = 5  # 每张图片的最大重试次数
            
            while retry_count < max_retries:
                try:
                    # 上传图片到 sm.ms 并获取 URL
                    img_url, delete_url = upload_img_to_smms(image_path)
                    
                    # 分析图片并获取响应
                    response_text = analyze_image_with_openai(img_url)
                    
                    # 打印响应并记录结果
                    print(response_text)
                    results.append({
                        "image_name": file,
                        "question": "What specific morphological features are visible in the cervical cells in this image?",
                        "response": response_text
                    })
                    
                    # 如果有删除链接，删除上传的图片
                    if delete_url:
                        delete_uploaded_image(delete_url)
                    
                    # 每次调用后等待 2 秒
                    time.sleep(2)
                    pbar.update(1)  # 更新进度条
                    break  # 如果成功，退出重试循环
                except (ConnectionRefusedError, ConnectionAbortedError) as e:
                    # 处理特定错误并进行重试
                    retry_count += 1
                    print(f"第 {retry_count} 次尝试失败: {e}")
                    if retry_count < max_retries:
                        print("重试中...")
                        time.sleep(2)  # 重试前等待 2 秒
                    else:
                        print("已达到最大重试次数，跳过此文件。")
                        pbar.update(1)  # 更新进度条，即使跳过文件
                except Exception as e:
                    # 处理其他未预见的错误
                    print(f"发生了一个意外错误: {e}")
                    pbar.update(1)  # 更新进度条，即使出错
                    break
    
    # 将结果写入 JSON 文件
    with open(results_file, 'w', encoding='utf-8') as f:
        dump(results, f, ensure_ascii=False, indent=4)


def upload_img_to_smms(img_file_path):
    """将图片上传到 sm.ms，如果成功则返回 URL 和删除链接。"""
    token = 'g6cmiRoNNS2ZnIJ5BhblBzPR5UycrYPy'
    url = 'https://sm.ms/api/v2/upload'
    params = {'format': 'json', 'ssl': True}  # 定义请求参数
    headers = {'Authorization': token}  # 在请求头中包含授权令牌

    try:
        # 打开要上传的图片文件
        files = {'smfile': open(img_file_path, 'rb')}
    except FileNotFoundError:
        # 处理文件不存在的情况
        print("文件不存在")
        return None, None

    # 发送 POST 请求上传图片
    response = post(url, headers=headers, files=files, params=params)
    response_json = loads(response.text)
    print(f"==>> 响应 JSON: {response_json}")

    try:
        # 检查上传是否成功
        if response_json['code'] == 'success':
            # 返回图片 URL 和删除链接
            return response_json['data']['url'], response_json['data'].get('delete')
        else:
            return response_json.get('images'), None  # 如果存在，则返回已有的图片 URL
    except KeyError:
        handle_upload_error(response_json['code'])
        return None, None


def handle_upload_error(error_code):
    """根据 sm.ms 的错误代码处理特定错误。"""
    if error_code == 'unauthorized':
        # 如果是未经授权访问（无效的令牌），则抛出错误
        raise ConnectionRefusedError(
            "未经授权的访问 - 请检查您的 API 令牌。")
    elif error_code == 'flood':
        # 如果达到上传限制，则抛出错误
        raise ConnectionAbortedError(
            "上传限制已超出 - 请稍后再试。")
    else:
        # 打印未知错误的消息
        print("图片上传过程中发生未知错误。")


def analyze_image_with_openai(image_url):
    """将图片 URL 发送到 OpenAI 模型并获取分析响应。"""
    # 调用 OpenAI API 分析图片
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What specific morphological features are visible in the cervical cells in this image?"},
                    {"type": "image_url", "image_url": {'url': image_url}},
                ],
            }
        ],
    )
    # 返回模型的文本响应
    return response.choices[0].message.content


def delete_uploaded_image(delete_url):
    """通过访问删除链接删除上传的图片。"""
    try:
        response = get(delete_url)
        if response.status_code == 200:
            print("图片已成功删除。")
        else:
            print(f"删除图片失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"删除图片时发生错误: {e}")


if __name__ == "__main__":
    main()
