'''
本程序目的是对比两个excel中指定位置单元格是否正确
其中一个excel为答案,一个为结果,当结果内容与答案不匹配,则记录在变量score中
当两个excel所有行均对比完成时,输出score写入结果excel指定位置
'''

import pandas as pd
import os
from tqdm import trange



def judge_answer(df_filepath, df_out_filepath):

    # 读取两个excel
    df = pd.read_excel(df_filepath)
    df_out = pd.read_excel(df_out_filepath)

    # 变量初始化
    score = 0
    print('\033[91m'+'score: ' + '\033[92m', score)

    # 逐行读取df中第三列内容,与df_out中第一列内容对比,相同则score+1,不同则score+0
    for i in trange(len(df)):
        # 仅仅读取df第三列单元格中前三个字符,如果其中包含No,则替换为No,否则替换为Yes
        if 'No' in df.loc[i, 'answer'][:3]:
            answer = 'no'
        elif 'Yes' or 'yes' in df.iloc[i, 'answer'][:3]:
            answer = 'yes'
        else:
            print('第'+str(i+1)+'行第三列内容不符合要求')
        # 比对两个excel中指定位置单元格是否相同,正确在当前行第三列写入1,错误写入0
         # 去除df_out中answer的空格,并忽略大小写,取前三个字符
        reply = df_out.loc[i, 'answer'].strip().lower()[:3]
        if answer == reply:
            score += 1
            print('正确,score ' + str(score)+' 现在是第'+str(i+1)+'行')
            # df_out.iloc[i, 2] = 1

        else:
            print('错误', '正确答案是'+answer+'，你的答案是' +
                  str(reply), '   现在是第'+str(i+1)+'行')
            # df_out.iloc[i, 2] = 0

    # 输出score
    print(f"==>> score: {score}")

    # 写入excel第六列第二行并保存
    df_out.loc[0, 'score'] = score
    df_out.to_excel(df_out_filepath, index=False)

    return True


if __name__ == '__main__':
    if judge_answer(
        'D:\研究生\任务3\题库\VQA\最终题库\is\is_vqa.xlsx',
        # ! 整个程序您只需改动下面一行,如果您测试的是is_vqa的话
            'D:\研究生\任务3\测试结果/vqa\is/qwen-vl-max.xlsx'):
        print('测试通过')
    else:
        print('测试失败')
