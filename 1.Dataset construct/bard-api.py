from bardapi import Bard, SESSION_HEADERS
import os

import requests

session = requests.Session()
token = ""
session.cookies.set("", "")
session.cookies.set( "", "")
session.cookies.set("", "")
session.headers = SESSION_HEADERS

# 逐行读取位于D:\研究生\任务3\题库\QA\QA题库(new)_modified.xlsx的excel文件的第二列和第三列
# 第二列为简化句子,第三列为问题
# 将第二列和第三列的内容传递给Bard API,让其比较两句话的差别,若两句话都出现了those,that等代词,但是句中未出现指代的原文,也需要指出,最后获取其返回的答案
# 将答案写入到excel文件的第四列
# 保存excel文件
# 关闭excel文件
# 重复上述步骤,直到excel文件读取完毕
# 退出程序
# 保存excel文件
# 现在开始写代码
# 导入所需的模块
import pandas as pd
import xlwings as xw


# 读取excel文件
df = pd.read_excel("")


# 上一次循环在哪一行结束
start_num = 0

# 循环读取第二,三列
for i in range(start_num,len(df)):
    

    # 获取第二列单元格值
    value1 = df.iloc[i, 1]

    # 获取第三列单元格值
    value2 = df.iloc[i, 2]

    # 如果值不为空
    if not pd.isnull(value1) and not pd.isnull(value2):
        
        print("当前所在行数: "+str(i+1)+"\n")
        
        # debug
        print("value1: "+value1+"\n")
        print("value2: "+value2+"\n")

        # 同时将命令输入给模型,让其比较两句话的差别,若两句话都出现了those,that等代词,但是句中未出现指代的原文,也需要指出,获取Bard API返回的答案
        input_text = "请指出" + value1 + "和" + value2 + "有什么区别,请把两句话改动的地方用英文原文回答,其余部分用中文回答?,若两句话都出现了those,that等代词,但是句中未出现指代的原文,也需要节选部分英文原文指出"
        bard = Bard(session=session,token=token)
        answer = bard.get_answer(input_text)['content']
        print(answer)
        # 将答案写入到第四列单元格中
        df.iloc[i, 3] = answer
        # 保存excel文件
        df.to_excel("modified.xlsx", index=False)


        
        