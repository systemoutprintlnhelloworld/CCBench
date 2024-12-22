import os
import openai
import pandas as pd

import pandas as pd
import re
import sys

#处理模型返回的文本
def process_reply(reply,startnum):
    replies = re.split("\n\n", reply)

    excel_line_list = []
    simplified_sentences_list = []
    questions_list = []
    answers_list = []
    doubts_list = []
    reasons_list = []
    

    pattern = re.compile(r"^[12345]\.\s(.*)")

 
    for i in range(0, len(replies), 5):
        if i+4 < len(replies):
            excel_line = [str(startnum)] 
            simplified_sentences = [pattern.match(line).group(1) for line in re.split("\n", replies[i]) if pattern.match(line)]
            questions = [pattern.match(line).group(1) for line in re.split("\n", replies[i+1]) if pattern.match(line)]
            answers = [pattern.match(line).group(1) for line in re.split("\n", replies[i+2]) if pattern.match(line)]
            doubts = [pattern.match(line).group(1) for line in re.split("\n", replies[i+3]) if pattern.match(line)]
            reasons = [pattern.match(line).group(1) for line in re.split("\n", replies[i+4]) if pattern.match(line)]

            # 保证每个段落都有同样的行数
            max_len = max(len(simplified_sentences), len(questions), len(answers), len(doubts), len(reasons))
            excel_line += [""] * (max_len - len(excel_line))
            simplified_sentences += [""] * (max_len - len(simplified_sentences))
            questions += [""] * (max_len - len(questions))
            answers += [""] * (max_len - len(answers))
            doubts += [""] * (max_len - len(doubts))
            reasons += [""] * (max_len - len(reasons))

            excel_line_list.extend(excel_line)
            simplified_sentences_list.extend(simplified_sentences)
            questions_list.extend(questions)
            answers_list.extend(answers)
            doubts_list.extend(doubts)
            reasons_list.extend(reasons)
            #
        else:
            raise ValueError(" excel line  "+str(startnum)+"  raise error,"+"Input format is not as expected.")

    return simplified_sentences_list, questions_list, answers_list, doubts_list, reasons_list, excel_line_list


# 主程序

# 防止该程序崩溃,启动时自动重启
import signal



openai.api_key = '' # your api key here

openai.api_base = ""


# 从文本文件和Excel文件中读取数据
with open("D:\\研究生\\任务3\\规划\\prompt-QA.txt", 'r', encoding='utf-8') as file:
    system_prompt = file.read()

df_q = pd.read_excel("D:\\研究生\\任务3\\题库\\QA题源.xlsx")


#将start_num 写入'"D:\研究生\任务3\规划\start.txt"'文件中,每次程序被中断后,从txt文件中读取start_num,并在每次循环结束时将start_num+1写入txt文件中
with  open("D:\研究生\任务3\规划\start_qa.txt", 'r', encoding='utf-8') as file:
    startnum = int(file.read())

'''

从第二行开始逐行处理数据
支持手动断点续传,excel line  2 对应 0

'''
for startnum in range(startnum, min(425, df_q.shape[0])):

    print('\n')

    print(str(startnum)+"/"+str(df_q.shape[0]))

    print('\n')

    # 从Excel文件中读取用户输入
    user_prompt = df_q.iloc[startnum, 0]


    print(f" excel line  {str(startnum + 2)}  " + user_prompt)
    # print(" excel line  "+str(i+2)+"  "+user_prompt)
    #  报错TypeError: can only concatenate str (not "float") to str 说明


    # 调用 GPT-4 进行文本补全
    response = openai.ChatCompletion.create(
      model = "gpt-4",
      messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
      ],
    )

    # 打印返回的completion.choices[0].message.content变量并保存到变量 reply中
    reply = response.choices[0].message.content
    print(reply)


    startnum = startnum + 1

    with  open("D:\研究生\任务3\规划\start_qa.txt", 'w', encoding='utf-8') as file:
        file.write(str(startnum-1))

    try:
        simplified_sentences_list, questions_list, answers_list, doubts_list, reasons_list ,excel_line_list= process_reply(reply,startnum)
        if len(simplified_sentences_list) == 0:
            print("excel line  "+str(startnum+1)+"  ,All lists are empty, nothing to write to Excel.")
        else:
            df_new = pd.DataFrame({
        'excel_line': excel_line_list,
        'simplified_sentences': simplified_sentences_list,
        'questions': questions_list,
        'answers': answers_list,
        'doubts': doubts_list,
        'reasons': reasons_list
    })

        # 指定你的xlsx文件路径
        file_path = "D:\研究生\任务3\题库\QA题库(new).xlsx"

        if os.path.exists(file_path):
            df_old = pd.read_excel(file_path)
            df_a = pd.concat([df_old, df_new])
        else:
            df_a = df_new

        df_a.to_excel(file_path, index=False)
    except ValueError as e:
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write("excel line  "+str(startnum+1)+"  "+"  error happened,Problematic reply:\n" + reply + "\n")
        sys.exit(1)








