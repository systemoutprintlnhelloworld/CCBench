import os
import pandas as pd

# 读取Excel文件，假设第一列是图片文件名的文本
df = pd.read_excel("D:\\研究生\\任务2\\TBS-web-独有\\V3\\V3.xlsx")

# 获取图片文件名列表
img_names = df.iloc[:,0].tolist()

# 获取图片文件夹路径
img_path = "D:\\研究生\\任务2\\TBS-web-独有\\V3\\jpg"



# 遍历图片文件名列表，找到对应的图片文件，并重命名为行号.jpg
for i, name in enumerate(img_names):
    # 根据'.jpg'分割文本，并取第一个元素作为图片文件名
    name = name.split('.jpg')[0] + '.jpg'
    # 拼接图片文件的完整路径
    img_file = os.path.join(img_path, name)
    # 判断图片文件是否存在
    if os.path.isfile(img_file):
        # 生成新的图片文件名，格式为行号.jpg
        new_name = str(i+1) + ".jpg"
        # 拼接新的图片文件的完整路径
        new_file = os.path.join(img_path, new_name)
        # 重命名图片文件
        os.rename(img_file, new_file)
    else:
        # 如果图片文件不存在，打印提示信息
        print(f"没有找到{name}这个图片文件")
