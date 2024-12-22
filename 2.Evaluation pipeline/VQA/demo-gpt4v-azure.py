import base64
from mimetypes import guess_type

from openai import AzureOpenAI

# 将本地图像编码为数据URL的函数
def local_image_to_data_url(image_path):
    # 根据文件扩展名猜测图像的MIME类型
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # 如果未找到MIME类型，则使用默认的MIME类型

    # 读取并编码图像文件
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(
            image_file.read()).decode('utf-8')

    # 构造数据URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

# 示例用法
image_path = r'D:\研究生\帮师兄评测模型\1.jpg'
data_url = local_image_to_data_url(image_path)
# print("Data URL:", data_url)

# 你的端点应如下所示：https://YOUR_RESOURCE_NAME.openai.azure.com/
api_base = ''
api_key = ""
deployment_name = 'gpt-4'
api_version = '2024-05-01-preview'  # 这个版本号在将来可能会发生变化

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    base_url=f"{api_base}openai/deployments/{deployment_name}/extensions",
)

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [
            {
                "type": "text",
                "text": "Describe this picture:"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64," + data_url
                }
            }
        ]}
    ],
    max_tokens=2000
)
print(response)
