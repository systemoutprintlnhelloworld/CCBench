import re
import openai
import pandas as pd

openai.api_key = '' # your api key here\
# 手动更换api,或者做成字典

openai.api_base = ""


#从'D:\研究生\任务2\压缩包\TBS-V3_book'中读取文本作为System Prompt,其读入顺序为 chapter-x(文件夹) -> txt(文件夹) -> Fig.x.y.txt (x为章节号,x>=4,x<=7，y为图号),遍历完一个txt文件夹下所有txt文件后，再退回上一级目录遍历hapter-x+1  (x>=4,x<=7)文件夹下的txt文件夹，直到遍历完所有chapter文件夹

#现在开始写这个深度优先遍历算法
#首先定义一个函数，用于遍历所有txt文件
import os

import sys

#定义一个进度条方法
def progress_bar(i, total):
    percent = (i / total) * 100
    sys.stdout.write('\r')
    sys.stdout.write("[%-20s] %d%%" % ('='*int(percent//5), percent))
    sys.stdout.flush()

# 写一个深度遍历方法,将4-7章文件夹下所有的txt文件夹路径(值)存入一个列表中,在每轮openai调用中,从列表中取出一个txt文件夹路径(值)从此处读入txt文件

#定义一个列表，用于存储所有txt文件夹路径
txt_path_list = []

allow_read_dir = []

#定义的方法还要有两个输入参数，一个是方法运行根目录，一个是允许读取根目录下哪些文件夹(chapter4-7)
def dfs(root_path,  allow_read_dir):
    #首先判断root_path是否为空，如果为空，直接返回
    if root_path == '':
        return
    #如果不为空，就读取root_path下的所有文件夹
    else:
        #读取root_path下的所有文件夹
        dir_list = os.listdir(root_path)
        #遍历dir_list，如果是文件夹，就判断是否在allow_read_dir中，如果在，就将其路径加入到txt_path_list中
        for dir in dir_list:
            #判断是否是文件夹
            if os.path.isdir(root_path+'\\'+dir):
                #判断是否在allow_read_dir中
                if dir in allow_read_dir:
                    #如果dir == 'txt',则进入该文件夹并把其中每一个txt文件的绝对路径加入到txt_path_list中
                    if dir == 'txt':
                        #进入该文件夹
                        txt_dir_list = os.listdir(root_path+'\\'+dir)
                        #遍历txt_dir_list，将其中每一个txt文件的绝对路径加入到txt_path_list中
                        for txt_dir in txt_dir_list:
                            txt_path_list.append(root_path+'\\'+dir+'\\'+txt_dir)
                    else:
                    #调用dfs方法，传入参数
                        dfs(root_path+'\\'+dir, allow_read_dir)
                else:
                    #如果不在allow_read_dir中，就跳过
                    # print(dir+"不在allow_read_dir中")
                    continue
            else:
                #如果不是文件夹，就跳过
                # print(dir+"不是文件夹")
                continue


#调用dfs方法，传入参数,根目录'D:\研究生\任务2\压缩包\TBS-V3_book'和允许读取的文件夹列表['chapter-2','chapter-4','chapter-5','chapter-6','chapter-7']
dfs('D:\研究生\任务2\压缩包\TBS-V3_book',['chapter-2','chapter-4','chapter-5','chapter-6','chapter-7','txt'])

#将openai回复写入excel文件中
def process_reply(reply,fig_name):
    replies = re.split("\n\n", reply)

    questions_list = []
    answers_list = []
    doubts_list = []
    reasons_list = []
    fig_name_list = []

    fig_name_list.append(fig_name)


    for i in range(0, len(replies)):
        #通过正则表达式筛选问题、答案、疑问、理由内的文本
        pattern = re.compile(r"^[12345]\.\s*(.*)")
        if i == 0:
            questions_sentence = [pattern.match(line).group(1) for line in re.split("\n", replies[i]) if pattern.match(line)]
            questions_list.extend(questions_sentence)
            
        elif i == 1:
            answers_sentence = [pattern.match(line).group(1) for line in re.split("\n", replies[i]) if pattern.match(line)]
            answers_list.extend(answers_sentence)
        elif i == 2:
            doubts_sentence = [pattern.match(line).group(1) for line in re.split("\n", replies[i]) if pattern.match(line)]
            doubts_list.extend(doubts_sentence)
        elif i == 3:
            reasons_sentence = [pattern.match(line).group(1) for line in re.split("\n", replies[i]) if pattern.match(line)]
            reasons_list.extend(reasons_sentence)
        else:
            raise ValueError("Input format is not as expected.")

    if len(questions_list) == 0 and len(answers_list) == 0 and len(doubts_list) == 0 and len(reasons_list) == 0:
        raise ValueError("All parts are empty.")
    else:
        if len(questions_list) == 0:
            print("Questions part is empty.")
        if len(answers_list) == 0:
            print("Answers part is empty.")
        if len(doubts_list) == 0:
            print("Doubts part is empty.")
        if len(reasons_list) == 0:
            print("Reasons part is empty.")
    
    max_len = max(len(questions_list), len(answers_list), len(doubts_list), len(reasons_list))

    questions_list += [""] * (max_len - len(questions_list))
    answers_list += [""] * (max_len - len(answers_list))
    doubts_list += [""] * (max_len - len(doubts_list))
    reasons_list += [""] * (max_len - len(reasons_list))
    fig_name_list += [""] * (max_len - len(fig_name_list))


    return questions_list, answers_list, doubts_list, reasons_list, fig_name_list



#输出列表的长度
# print(len(txt_path_list))

#循环167次，每次读入一个txt文件，然后将其加入到user_prompt中
user_prompt = ''

# 位于"D:\研究生\任务3\规划\prompt-VQA.txt"中的文本作为System Prompt
with open("D:\\研究生\\任务3\\规划\\prompt-VQA.txt", 'r', encoding='utf-8') as file:
    system_prompt = file.read()

#循环读取txt文件的文件名
fig_name = ''


#将start_num 写入'"D:\研究生\任务3\规划\start.txt"'文件中,每次程序被中断后,从txt文件中读取start_num,并在每次循环结束时将start_num+1写入txt文件中
with  open("D:\研究生\任务3\规划\start.txt", 'r', encoding='utf-8') as file:
    start_num = int(file.read())


#循环列表长度次数
for start_num in range(start_num,len(txt_path_list)):
    
    #做一个可视化的进度条,显示当前处理进度
    progress_bar(start_num, (len(txt_path_list)))
    print('     目前进度 : '+str(len(txt_path_list))+'/'+str(start_num))
    
    #读入txt文件名
    fig_name = os.path.basename(txt_path_list[start_num])
    #换行输出此时的fig_name
    print('\n')
    print('此时读入的图片名称 '+fig_name)
    print('\n')
    #循环调用方法,读入txt文件
    
    with open(txt_path_list[start_num], 'r', encoding='utf-8') as file:
        user_prompt = file.read()


    #debug
    print('此时读入的用户输入 '+user_prompt)
    print('\n')
    # print(system_prompt)
    # print('\n')

    start_num += 1

    #以上几项出错概率低,在这里写入start_num进txt文件中
    with  open("D:\研究生\任务3\规划\start.txt", 'w', encoding='utf-8') as file:
        file.write(str(start_num-1))


    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[
            {"role": "system", "content": system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]
    )

    reply = response.choices[0].message.content
    
    try:
        questions_list, answers_list, doubts_list, reasons_list,fig_name_list = process_reply(reply,fig_name)

        # print (questions_list)
        # print (answers_list)
        # print (doubts_list)
        # print (reasons_list)
        # print (fig_name_list)
        
        df_new = pd.DataFrame({
            'questions': questions_list,
            'answers': answers_list,
            'doubts': doubts_list,
            'reasons': reasons_list,
            'fig_name': fig_name_list
        })
        

        # 指定你的xlsx文件路径
        file_path = "D:\研究生\任务3\题库\VQA题库(new).xlsx"

        if os.path.exists(file_path):
            df_old = pd.read_excel(file_path)
            df = pd.concat([df_old, df_new])
        else:
            df = df_new

        df.to_excel(file_path, index=False)
    except ValueError as e:
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write("Problematic reply:\n" + reply + "\n")
        sys.exit(1)