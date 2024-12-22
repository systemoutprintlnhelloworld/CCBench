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
import openai

openai.api_type = "azure"
openai.api_version = "2023-05-15"

openai.api_base = ""
openai.api_key = ""

# 初始化变量
is_repeat = False
score = 0
# 如excel第27列,这里应该写第25列
start_num = 62
end_num = 63

accuracy = 0
# 导入进度条包


def tdlm_progress(start_num, total_steps, name="操作"):

    with tqdm.tqdm(total=total_steps, desc=name, unit="条", initial=start_num) as pbar:

        pbar.update(1)

# 逐行读取位于'D:\研究生\任务3\题库\QA\最终版\is\is_qa.xlsx'中第一行的问题,并调用gpt4进行回答


# 读取位于'D:\研究生\任务3\题库\QA\最终版\is\is_qa.xlsx'中的excel
df = pd.read_excel('D:\研究生\任务3\题库\QA\最终版\is\is_qa.xlsx',
                   sheet_name='Sheet1')  # ^ open/is题型切换时需要修改

# 输出位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel
df_out = pd.read_excel(
    'D:\研究生\任务3\测试结果\QA\is\gpt-4.xlsx', sheet_name='Sheet1')  # ^ open/is题型切换时需要修改

# 读取位于'D:\研究生\任务3\提示词\qa-sys-is-prompt.txt'的提示词作为系统提示
with open('D:\研究生\任务3\提示词\qa-sys-is-prompt.txt', 'r', encoding='utf-8') as f:  # ^ open/is题型切换时需要修改
    prompt = f.read()

# 构造例子,作为user/assistant角色进行少样本学习

# ~ open题型需要注释掉下面这行
question_example = 'Q: Is the background of this picture not black?'
answer_example = '{'\
    '"reason":"The background of this picture is white, not black.",'\
    '"answer":"Yes"'  \
    '}'

# ~ is题型需要注释掉下面这行
# question_example = 'Q: What is the nucleoplasmic ratio of the cells shown in this image?'
# answer_example = '{'\
#     '"reason":"Based on the information in the image, the cytoplasm is very close to the nucleus.",'\
#     '"answer":"close to 1"'  \
#     '}'


# debug
print('question_example'+question_example)
print("answer_example:"+answer_example)

# 开始循环读取excel中的问题,并调用gpt4进行回答,直到读取到excel中的最后一行
# excel读到最后一行则停止循环
for start_num in range(start_num, end_num):
# for start_num in range(start_num, len(df)):
    # 显示进度条
    tdlm_progress(start_num, len(df), name="回答进度")
    # 从第二行开始
    # 读取第一列的问题
    question = df.iloc[start_num, 1]

    # 读取第二列的ground_truth
    # ~ open题型需要注释掉下面这行
    ground_truth = df.iloc[start_num, 2]

    # debug
    print(question)
    print('question:'+str(question))

    # ~ open题型需要注释掉下面这行
    print('ground_truth:'+ground_truth)

    # 量化ground_truth,其中前三个字母为'Yes'则量化为1,前三个字母包含'No'则量化为0,如果没有三个字母则只取两个字母
    # 截取ground_truth中前三个字母

    # ~ open题型需要注释掉下面很多
    ground_truth = ground_truth[0:3]
    if len(ground_truth) == 3:
        if ground_truth[0:3] == 'Yes':
            ground_truth = 1
        elif 'No' in ground_truth[0:3]:
            ground_truth = 0
        else:
            print('ground_truth前三个字母不匹配错误')
            print('start_num:'+str(start_num))
            print('准确率:'+str(accuracy))
            exit  # !结束程序运行
        # 如果ground_truth的长度为2,则只需判断是否为No
    elif len(ground_truth) == 2:
        if ground_truth[0:2] == 'No':
            ground_truth = 0
        else:
            print('ground_truth 前二字母不匹配错误')
            print('start_num:'+str(start_num))
            print('准确率:'+str(accuracy))
            exit  # !结束程序运行
    else:
        print('ground_truth长度异常')
        print('start_num:'+str(start_num))
        print('准确率:'+str(accuracy))
        exit  # !结束程序运行

    # 初始化强调格式输入命令,该命令仅仅在本次循环出现错误时使用
    sys_reminder_false = 'please pay attention to the format of your respond in json format,and answer must be english ,reason must be chinese'
    sys_reminder_true = ""
    if is_repeat:
        sys_reminder_true == sys_reminder_false
    # 将prompt作为系统提示词,question_example作为用户输入,answer_example作为assistant回答,question作为用户输入
    try:
        response = openai.ChatCompletion.create(
            engine='gpt-4',
            messages=[
                {"role": "system", "content": sys_reminder_true},
                {"role": "system", "content": prompt},
                {"role": "user", "content": question_example},
                {"role": "assistant", "content": answer_example},
                {"role": "user", "content": question},
            ]
        )
        # print the response
        print("GPT对于第"+str(start_num)+"个问题的回答是" +
              response['choices'][0]['message']['content'])

    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")

    except openai.error.AuthenticationError as e:
        # Handle Authentication error here, e.g. invalid API key
        print(f"OpenAI API returned an Authentication Error: {e}")

    except openai.error.APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")

    except openai.error.InvalidRequestError as e:
        # Handle connection error here
        print(f"Invalid Request Error: {e}")

    except openai.error.RateLimitError as e:
        # Handle rate limit error
        print(f"OpenAI API request exceeded rate limit: {e}")

    except openai.error.ServiceUnavailableError as e:
        # Handle Service Unavailable error
        print(f"Service Unavailable: {e}")

    except openai.error.Timeout as e:
        # Handle request timeout
        print(f"Request timed out: {e}")

    except:
        # Handles all other exceptions
        print("An exception has occured.")

    # 读取完毕,现在提取回复的json格式的reason和answer,如果不符合格式则需要重新回答这个问题
    # 拆解json
    import json

    response_processed = response['choices'][0]['message']['content']

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
        # 用空字符串替换最后一个"和最后一个}之间的字符
        response_processed = response_processed[:last_quote +
                                                1] + response_processed[last_brace:]

    # 将response进行处理,首先将其转化为字典,替换掉reson键对应的值中多余的双引号为单引号
    response_processed = response_processed.replace(
        '"reason":"""', "'reason':'").replace('"""', "'")
    # 将response进行处理,将其转化为字典,替换掉answer键对应的值中多余的双引号为单引号
    response_processed = response_processed.replace(
        '"answer":"""', "'answer':'").replace('"""', "'")
    # 去除掉其中的所有换行符
    response_processed = response_processed.replace('\n', '')

    response_json = json.loads(response_processed)
    # 重置is_repeat
    is_repeat = False

    # ~ open题型需要注释掉下面这些
    # 检查json中是否有reason和answer,并且reason是中文而不是英文,answer是'Yes'或'No'(大小写均可)
    if 'reason' not in response_json or 'answer' not in response_json or response_json['reason'] == '' or response_json['answer'] not in ['Yes', 'No', 'yes', 'no']:
        is_repeat = True  # 加上强调语句
        start_num = start_num-1  # 重新回答这个问题
        print('response或answer格式错误')
        continue  # *跳出本次循环

    # 提取reason
    reason = response_json['reason']

    # 去除换行符
    # 提取answer
    answer = response_json['answer']

    # debug
    print('reason:'+reason)
    print('answer:'+answer)
    print('start_num:'+str(start_num))

    # 将response中的reason和answer写入位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel的第二列和第一列中
    df_out.iloc[start_num, 1] = reason
    df_out.iloc[start_num, 0] = answer

    # 保存excel
    df_out.to_excel('D:\研究生\任务3\测试结果\QA\is\gpt-4.xlsx',
                index=False)  # ^ open/is题型切换时需要修改

    # ~ open题型需要注释掉下面这些
    # 量化answer,如果是'yes'则量化为1,如果是'no'则量化为0(大小写均可)
    if answer.lower() == 'yes':
        answer = 1
    elif answer.lower() == 'no':
        answer = 0
    else:
        print('answer格式错误')
        start_num -= start_num  # 重新回答这个问题
        continue  # *跳出本次循环
    # 比对answer和ground_truth,如果不一致则记录变量score增加0,如果一致则记录变量score增加1
    if answer == ground_truth:
        # 将该次回答是否正确写入位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel的第三列中
        df_out.iloc[start_num, 2] = 1

        score = score+1
    else:
        # 将该次回答是否正确写入位于'D:\研究生\任务3\测试结果\QA\gpt-4.xlsx'中的excel的第三列中
        df_out.iloc[start_num, 2] = 0

        score = score+0
    # 计算当前正确率
    accuracy_current = score/start_num
    # debug
    # ~open题型需要注释掉下面这行
    print('accuracy:'+str(accuracy))

# 计算正确率
# ~open题型需要注释掉下面这些
accuracy = score/(len(df))
# 写入df_out的第五列
df_out.iloc[1, 4] = accuracy

# 保存
df_out.to_excel('D:\研究生\任务3\测试结果\QA\is\gpt-4.xlsx',
                index=False)  # ^ open/is题型切换时需要修改
