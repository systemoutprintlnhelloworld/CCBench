# 导入所需的模块
import pandas as pd
import os
import xlwings as xw

# 读取excel文件
df = pd.read_excel("D:\研究生\任务3\题库\VQA\VQA题库(new)_modified.xlsx")

# 循环读取第六列
for i in range(len(df)):
    # 如果该列某行对应列单元格内容为空
    if pd.isnull(df.iloc[i, 7]):
        # 修改其值等于其上行该列第一个值不为空的单元格值
        df.iloc[i, 7] = df.iloc[i-1, 7]

# 循环读取第六列
for i in range(len(df)):
    # 获取该列单元格值
    value = df.iloc[i, 7]
    # 如果值不为空
    if not pd.isnull(value):
        # 去除后缀
        value = value[:-4]
        # 按照"."分割
        value = value.split(".")
        # 获取章节编号
        chapter = value[1][-1]
        # 获取文件名
        filename = ".".join(value)
        # 拼接相对路径
        path = r"txt/chapter-" + chapter + r"/txt/" + filename + r".txt"

        # 将其第6列单元格变为超链接
        df.iloc[i, 7] = '=HYPERLINK("' + path + '","' + filename + '")'

# 循环读取第七列
for i in range(len(df)):
    # 获取第六列同行单元格值(此时这里显示的是超链接,我们需要获取超链接中属性:显示的文字的值,而不是其链接的值)
    # 如 此时单元格值为 '=HYPERLINK("txt/chapter-2/txt/Fig.2.1.txt","Fig.2.1")',我们需要获取的是"Fig.2.1"
    # 下面对其进行分割
    value = df.iloc[i, 7].split('"')[3]
    
    # 如果值不为空
    if not pd.isnull(value):
        # 修改其后缀为.jpg
        value = value + ".jpg"
        # 拼接相对路径
        path = "img/" + value
        # debug
        print(path)
        # 将该值转移到同行第7列单元格中
        df.iloc[i, 8] = value
        # 将其转为变为超链接
        df.iloc[i, 8] = '=HYPERLINK("' + path + '","' + value + '")'

# 将修改后的数据框保存为新的excel文件
df.to_excel("D:\研究生\任务3\题库\VQA\VQA题库(new)_modified_new.xlsx", index=False)

# 打开新的excel文件
app = xw.App(visible=True, add_book=False)
wb = app.books.open("D:\研究生\任务3\题库\VQA\VQA题库(new)_modified_new.xlsx")
