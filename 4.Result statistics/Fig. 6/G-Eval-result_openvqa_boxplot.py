import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 宽12，高24
fig, axs = plt.subplots(1, 1, figsize=(12, 24))

# 读取excell第五列
source = r"D:\研究生\任务3\程序输出\open-vqa-gpt评分\章节统计\open-vqa-评估结果 - 章节统计-format.xlsx"
df = pd.read_excel(source)

# 一共四个模型bard,gpt-4,Ilava,qwen-vl-max,创造一个json,收集并聚集第二列匹配对应模型名这一行的的第五列的值
data = {'bard': [], 'gpt-4': [], 'llava': [], 'qwen-vl-max': []}
for i in range(0, len(df)):
    if df.iloc[i, 1] == 'bard':
        data['bard'].append(df.iloc[i, 4])
    elif df.iloc[i, 1] == 'gpt-4':
        data['gpt-4'].append(df.iloc[i, 4])
    elif df.iloc[i, 1] == 'llava':
        data['llava'].append(df.iloc[i, 4])
    elif df.iloc[i, 1] == 'qwen-vl-max':
        data['qwen-vl-max'].append(df.iloc[i, 4])


# 生成箱形图
all_data = [data['gpt-4'], data['bard'], data['llava'], data['qwen-vl-max']]

# 使用平均值进行比对
bplot = axs.boxplot(all_data, meanline=True,
                    showcaps=True,
                    showfliers=False,
                    showmeans=True,
                    patch_artist=True,
                    medianprops=dict(color="orange"))  # 设置中值线为橙色

# 返回其中的medians并打印
medians = bplot['medians']
for median in medians:
    print(median.get_ydata()[0])

for median in bplot['medians']:
    median.set_visible(False)
    
axs.set_ylim([-0.05, 1.05])  # 设置y轴范围为0到1
axs.set_title('Correctness')

plt.rcParams['font.sans-serif'] = ['Times New Roman']
plt.rcParams['axes.facecolor'] = 'white'
axs.grid(False)
plt.rcParams['font.sans-serif'] = ['Times New Roman']

labels = ['GPT-4V', 'Bard', 'LlVa', 'Qwen-VL']
colors = ["#FDC897", "#9DD79D", "#C2B2D6", "#FFFFA2"]

# 填充颜色
for patch, color in zip(bplot['boxes'], colors):
    patch.set_facecolor(color)

axs.yaxis.grid(False)
axs.set_xticks([y + 1 for y in range(len(all_data))],
               labels=['GPT-4V', 'Bard', 'LLaVa', 'Qwen-VL'])
axs.tick_params(axis='x', rotation=25)
axs.set_ylabel('Score')

axs.spines['top'].set_visible(False)
axs.spines['right'].set_visible(False)
# plt.savefig(r"D:\研究生\任务3\论文作图\result-open-vqa-箱形图-test2.svg", format='svg')

# 将各个model的 Mean Std lower upper 保存到excel
mean = []
std = []
lower = []
upper = []
for i in range(4):
    mean.append(np.mean(all_data[i]))
    std.append(np.std(all_data[i]))
    lower.append(np.percentile(all_data[i], 25))
    upper.append(np.percentile(all_data[i], 75))
data = {'Model': ['GPT-4V', 'Bard', 'LLaVa', 'Qwen-VL'],
        'Mean': mean,
        'Std': std,
        'Lower': lower,
        'Upper': upper}
df = pd.DataFrame(data)
df.to_excel(r"D:\研究生\任务3\论文作图\result-open-vqa-箱形图-test2.xlsx", index=False)