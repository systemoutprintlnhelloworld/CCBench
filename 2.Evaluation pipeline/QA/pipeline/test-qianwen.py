__updated__ = '2024-06-21 21:26:39'

# 调用azure openai api ,对excel逐行问题进行回答

# ? 目前放弃了:
# 1.思维链
# 2.引导输出
# 3.shuffle打乱题库题目顺序(不需要)

'''
# & 本程序运行流程:
调用模型接口测试题目
得到回答,统计正确率
将reason,answer,accuracy记录到excel中
'''

import tqdm
import pandas as pd
import random
from http import HTTPStatus
import dashscope
import logging
import json

dashscope.api_key = ""

# 初始化变量
is_repeat = False
score = 0
# ^ 程序中断时修改,如中断于excel第27列,这里应该写第26列
start_num = 

accuracy = 0
flag = False
is_json = True

# 逐行读取位于'D:\研究生\任务3\题库\QA\最终版\is\is_qa.xlsx'中第一行的问题,并调用gpt4进行回答


# 读取位于'D:\研究生\任务3\题库\QA\最终版\is\is_qa.xlsx'

df = pd.read_excel('D:\研究生\任务3\题库\QA\最终版\open\open_qa.xlsx',
                   sheet_name='Sheet1')  # ^ open/is题型切换,或切换模型时需要修改

# 输出位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel
df_out = pd.read_excel(
    'D:\研究生\任务3\测试结果\QA\open\通义千问.xlsx', sheet_name='Sheet1')  # ^ open/is题型切换时需要修改

# 配置进度条,每轮循环更新一次其参数


def tdlm_progress(start_num, total_steps, name="操作"):
    # 配置速度:3条每70秒
    with tqdm.tqdm(total=total_steps, desc=name, initial=start_num) as pbar:
        pbar.set_description(
            f"Processing {start_num}, avg time: {pbar.dynamic_miniters: .4f}")
        pbar.update(1)


# 读取位于'D:\研究生\任务3\提示词\qa-sys-is-prompt.txt'的提示词作为系统提示
with open('D:\研究生\任务3\提示词\qa-sys-open-prompt.txt', 'r', encoding='utf-8') as f:  # ^ open/is题型切换时需要修改
    prompt = f.read()

# 构造例子,作为user/assistant角色进行少样本学习

# ~ open题型需要注释掉下面这行
# question_example = 'Is the background of this picture not black?'
# answer_example = '{'\
#     '"reason":"The background of this picture is white, not black.",'\
#     '"answer":"Yes"'  \
#     '}'

# ~ is题型需要注释掉下面这行
question_example = 'What is the nucleoplasmic ratio of the cells shown in this image?'
answer_example = '{'\
    '"reason":"Based on the information in the image, the cytoplasm is very close to the nucleus.",'\
    '"answer":"close to 1"'  \
    '}'


# debug
print('question_example'+question_example)
print("answer_example:"+answer_example)

# 开始循环读取excel中的问题,并调用gpt4进行回答,直到读取到excel中的最后一行
# excel读到最后一行则停止循环
for start_num in range(start_num, len(df)):

    # 正常情况下,执行一次循环,flag从True变为False,不需要重新回答这个问题
    flag = True

    # 当flage为True时,重复回答这个问题
    while flag:
        # 重置flag
        flag = False
        # 通过flag判断是否需要重新回答这个问题
        # 显示进度条
        tdlm_progress(start_num, len(df), "当前进度")
        # 从第二行开始
        # 读取第一列的问题
        question = df.iloc[start_num, 2]

        # 读取第二列的ground_truth
        # ~ open题型需要注释掉下面这行
        # ground_truth = df.iloc[start_num, 1]

        # debug
        print('question:'+question)

        # ~ open题型需要注释掉下面这行
        # print('ground_truth:'+ground_truth)

        # 量化ground_truth,其中前三个字母为'Yes'则量化为1,前三个字母包含'No'则量化为0,如果没有三个字母则只取两个字母
        # 截取ground_truth中前三个字母

        # ~ open题型需要注释掉下面很多
        # ground_truth = ground_truth[0:3]
        # if len(ground_truth) == 3:
        #     if ground_truth[0:3] == 'Yes':
        #         ground_truth = 1
        #     elif 'No' in ground_truth[0:3]:
        #         ground_truth = 0
        #     else:
        #         print('ground_truth前三个字母不匹配错误')
        #         print('start_num:'+str(start_num))
        #         print('准确率:'+str(accuracy))
        #         exit  # !结束程序运行
        #     # 如果ground_truth的长度为2,则只需判断是否为No
        # elif len(ground_truth) == 2:
        #     if ground_truth[0:2] == 'No':
        #         ground_truth = 0
        #     else:
        #         print('ground_truth 前二字母不匹配错误')
        #         print('start_num:'+str(start_num))
        #         print('准确率:'+str(accuracy))
        #         exit  # !结束程序运行
        # else:
        #     print('ground_truth长度异常')
        #     print('start_num:'+str(start_num))
        #     print('准确率:'+str(accuracy))
        #     exit  # !结束程序运行
        # ~ 到此处结束注释

        # 初始化强调格式输入命令,该命令仅仅在本次循环出现错误时使用
        # ~ open题型需要注释掉下面这行
        # sys_reminder_false = 'please pay attention to the format of your respond in json format,and answer must be english ,reason must be chinese,and "answer"must be "Yes" or "No"'
        # ~ is题型需要注释掉下面这行
        sys_reminder_false = 'please pay attention to the format of your respond in json format,and answer must be english ,reason must be chinese'

        sys_reminder_true = " "
        if is_repeat:
            sys_reminder_true == sys_reminder_false
        # 将prompt作为系统提示词,question_example作为用户输入,answer_example作为assistant回答,question作为用户输入
        messages = [
            {"role": "system", "content": sys_reminder_true + prompt},
            {"role": "user", "content": question_example},
            {"role": "assistant", "content": answer_example},
            {"role": "user", "content": question}
        ]
        try:
            response = dashscope.Generation.call(
                dashscope.Generation.Models.qwen_max,
                messages= messages,
                # set the random seed, optional, default to 1234 if not set
                seed=random.randint(1, 10000),
                result_format='text',  # set the result to be "message" format. 
            )

            if response.status_code == HTTPStatus.OK:
                print(response)
            else:
                print(f'Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                    response.request_id, response.status_code,
                    response.code, response.message
                ))
            
            # 将GenerationResponse对象转换为一个JSON格式的字符串
            response = json.dumps(response)
            
            # 将字符串转换为Python字典
            data = json.loads(response)

            # 获取第一个choice的message
            response_processed = data['output']['text']

            # print the response
            print("通义千问对于第"+str(start_num)+"个问题的回答是" +
                  response_processed)

        except BaseException as e:
            print('\033[91m'+'报错: ' + '\033[92m', e)

        # 读取完毕,现在提取回复的json格式的reason和answer,如果不符合格式则需要重新回答这个问题
        # 拆解json
   
    
    
        # 将{}之外的内容全部清除
        # 找到第一个{的位置
        first_brace = response_processed.find('{')
        # 找到最后一个}的位置
        last_brace = response_processed.rfind('}')

        while True:
            # 如果其距离差小于10,则格式出现异常
            if last_brace - first_brace < 10:
                is_repeat = True  # 加上强调语句

                print('整个json格式输出错误')
                logging.basicConfig(
                    filename='D:\研究生\任务3\测试结果\QA\open\日志/qianwen-open.log', level=logging.DEBUG)  # ^ 模型切换时需要修改
                logging.debug("错误形式:整个json格式输出错误")
                is_json = False  # 标记为非json格式进行保存
                break  # *确认不是json形式的输出格式直接写入excel

             # 将这两个位置之间的字符替换为空字符串
            response_processed = response_processed[first_brace:last_brace+1]

            # 去除所有换行符
            response_processed = response_processed.replace('\n', '')

            # 将response进行处理,去除掉}之前,"之后,中间存在的逗号

            def is_valid(s):
                # 找到最后一个"的位置
                last_quote = s.rfind('"')
                # 找到最后一个}的位置
                last_brace = s.rfind('}')
                # 如果最后一个"与最后一个}距离相差大于1,则不满足条件
                if last_brace - last_quote > 1:
                    return False
                # 否则，满足条件
                else:
                    return True

            if not is_valid(response_processed):
                # 找到最后一个"的位置
                last_quote = response_processed.rfind('"')
                # 找到最后一个}的位置
                last_brace = response_processed.rfind('}')
                # 如果两者距离小于5,则认为可以替换
                if last_brace - last_quote < 4:
                    print("last_brace:"+str(last_brace))
                    print("last_quote"+str(last_quote))

                    # 用空字符串替换最后一个"和最后一个}之间的字符
                    response_processed = response_processed[:last_quote +
                                                            1] + response_processed[last_brace:]
                else:
                    is_repeat = True  # 加上强调语句
                    print('answer格式问题')
                    logging.basicConfig(
                        filename='D:\研究生\任务3\测试结果\QA\open\日志/qianwen-open.log', level=logging.DEBUG)  # ^ 模型切换时需要修改
                    logging.debug("错误形式:answer格式问题")
                    is_json = False  # 标记为非json格式进行保存
                    break
            # 将reason的值中的双引号变为单引号
            # 定位第三个"的位置
            third_quote = response_processed.find(
                '"', response_processed.find('"') + 1) + 1
            # third_quote = response_processed.find(
            #     '"', response_processed.find('"')+1, response_processed.rfind('"'))
            # 定位最后一个,的位置
            last_comma = response_processed.find('","')+2
            if last_comma == 1 :
                last_comma = response_processed.find('", "')+2
                print("特殊格式!")
            # 定位这个逗号左边出现的第一个"的位置
            last_quote = response_processed.rfind('"', 0, last_comma)
            # 将这两个位置之间的双引号替换为单引号
            response_processed = response_processed[:third_quote+3]+response_processed[third_quote+3:last_quote].replace(
                '"', "'")+response_processed[last_quote:]

            # ! 这里无需处理,这样反而能暴露gpt回答的问题
            # # 将response进行处理,answer的值只保留yes/no:实现方式:定位最后一个o/s(不区分大小写)的出现位置,再定位最后一个出现的"的位置,将这两个位置之间的字符替换为空字符串
            # # 找到最后一个o的位置
            # last_o = response_processed.rfind('o')
            # # 找到最后一个s的位置
            # last_s = response_processed.rfind('s')
            # # 判断哪个的位置更靠后,则将其作为最后一个出现的o/s
            # if last_o > last_s:
            #     last = last_o
            # else:
            #     last = last_s
            # # 找到最后一个"的位置
            # last_quote = response_processed.rfind('"')
            # # 将这两个位置之间的字符替换为空字符串
            # response_processed = response_processed[:last +
            #                                         1] + response_processed[last_quote:]

            # 去除掉其中的所有换行符
            response_processed = response_processed.replace('\n', '')

            # debug
            print("response_processed  "+response_processed)

            try:
                response_json = json.loads(response_processed)
            except BaseException:
                print("exception:"+str(Exception))
                print("json格式存在错误")
                is_json = False  # 标记为非json格式进行保存
                flag = True  # 让模型重新回复
                logging.basicConfig(
                    filename='D:\研究生\任务3\测试结果\QA\is\日志/qianwen-is.log', level=logging.DEBUG)  # ^ 模型切换时需要修改
                # 建立excel行对start_num的映射
                logging.debug('start_num:'+str(start_num+2)+"json格式存在错误")
                logging.error("response_processed"+response_processed)
                logging.debug('question:'+question)
                logging.debug("\n")
                break
            # 重置is_repeat
            is_repeat = False

            # ~ open题型需要注释掉下面这些
            # # 检查json中是否有reason和answer
            # if 'reason' not in response_json or 'answer' not in response_json or response_json['reason'] == '':
            #     is_repeat = True  # 加上强调语句
            #     flag = True  # 重新回答这个问题
            #     print('response或answer格式错误')
            #     continue  # *跳出本次循环
            # ~ 到此处结束注释
            # 提取reason
            reason = response_json['reason']

            # 去除换行符
            # 提取answer
            answer = response_json['answer']

            # debug
            print('reason:'+reason)
            if answer:

                print('answer:'+answer)
            print('start_num:'+str(start_num))

            # 将response中的reason和answer写入位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel的第二列和第一列中
            df_out.iloc[start_num, 1] = reason
            df_out.iloc[start_num, 0] = answer
            df_out.to_excel('D:\研究生\任务3\测试结果\QA\open/通义千问.xlsx',
                            index=False)  # ^ open/is题型切换时需要修改
            is_json = True
            break

        # 保存excel

        if is_json == False:
            df_out.iloc[start_num, 0] = response_processed  # 保存到第一格中,稍后进行筛选
            is_repeat == True  # 防止下次再不按规定输出非json格式

            # 记入日志
            logging.basicConfig(
                filename='D:\研究生\任务3\测试结果\QA\open\日志/qianwen-open.log', level=logging.DEBUG)  # ^ 模型切换时需要修改
            # 建立excel行对start_num的映射
            logging.debug('start_num:'+str(start_num+2)+"输出格式错误")
            logging.error("response_processed"+response_processed)
            logging.debug('question:'+question)
            logging.debug("\n")

        df_out.to_excel('D:\研究生\任务3\测试结果\QA\open\通义千问.xlsx',
                        index=False)  # ^ open/is题型切换时需要修改
        if is_json:

            print("格式正确!")
            # ~ open题型需要注释掉下面这些
            # # 量化answer,如果是'yes'则量化为1,如果是'no'则量化为0(大小写均可)
            # if answer.lower().find('yes') != -1:
            #     answer = 1
            # elif answer.lower().find('no') != -1:
            #     answer = 0
            # else:
            #     print('answer格式错误')
            #     # 记入日志
            #     logging.basicConfig(
            #         filename='D:\研究生\任务3\测试结果\QA\open\日志/qianwen-open.log', level=logging.DEBUG)  # ^ 模型切换时需要修改

            #     # 建立excel行对start_num的映射
            #     logging.debug('start_num:'+str(start_num+2)+"answer格式错误")
            #     logging.debug('reason:'+reason)
            #     logging.debug('answer:'+answer)
            #     logging.debug('question:'+question)
            #     answer = "error"
            # # 比对answer和ground_truth,如果不一致则记录变量score增加0,如果一致则记录变量score增加1
            # if answer == ground_truth:
            #     # 将该次回答是否正确写入位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel的第三列中
            #     print('回答正确')
            #     # DEBUG
            #     print('answer:'+str(answer))
            #     print('ground_truth:'+str(ground_truth))
            #     df_out.iloc[start_num, 2] = 1

            #     score = score+1
            # else:
            #     # 将该次回答是否正确写入位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel的第三列中
            #     df_out.iloc[start_num, 2] = 0
            #     print('回答错误')
            #     score = score+0

            # # 保存
            # df_out.to_excel('D:\研究生\任务3\测试结果\QA\is\通义千问.xlsx',
            #                 index=False)  # ^ open/is题型或模型切换时需要修改
            # # 计算当前正确率
            # accuracy_current = score/(start_num+1)
            # # debug
            # print('当前正确率:'+str(accuracy_current))
            # ~到此处结束注释


# 计算正确率
# ~open题型需要注释掉下面这行
# accuracy = score/(len(df))
# # 写入df_out的第五列
# df_out.iloc[0, 4] = accuracy

# 保存
df_out.to_excel('D:\研究生\任务3\测试结果\QA\open\通义千问.xlsx',
                index=False)  # ^ open/is题型或模型切换时需要修改
