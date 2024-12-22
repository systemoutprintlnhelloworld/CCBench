import pandas as pd
from scipy.stats import spearmanr
from scipy import stats

# 读取 Excel 文件
df = pd.read_excel(
    r'D:\研究生\任务3\supplementary\Fig. 6\支撑数据\open-vqa-汇总(陈医生版).xlsx', engine='openpyxl')

# 提取评分列
expert1_scores = df.iloc[:, 0:4]  # 专家1评分 A-D列
expert2_scores = df.iloc[:, 4:8]  # 专家2评分 E-H列
expert3_scores = df.iloc[:, 8:12]  # 专家3评分 I-L列

def calculate_kendalltau(df, expert1_scores, expert2_scores, expert3_scores):
      kendalltau_results = []
      for i in range(len(df)):
        # 获取每个问题的评分
        expert1 = expert1_scores.iloc[i]
        expert2 = expert2_scores.iloc[i]
        expert3 = expert3_scores.iloc[i]
        
        if i == 20 :
            print('11')
        # 计算专家之间的kendalltau相关系数
        Tau_12 = stats.kendalltau(expert1, expert2)
        Tau_13 = stats.kendalltau(expert1, expert3)
        Tau_23 = stats.kendalltau(expert2, expert3)
        
        # 将每个问题的相关系数存储
        kendalltau_results.append([Tau_12.correlation, Tau_13.correlation, Tau_23.correlation])

        # 创建结果DataFrame
        kendalltau_df = pd.DataFrame(kendalltau_results, columns=[
                                'Expert1 vs Expert2', 'Expert1 vs Expert3', 'Expert2 vs Expert3'])

        # 计算每个专家的平均Spearman相关系数
        avg_tau_expert1 = (kendalltau_df['Expert1 vs Expert2'].mean() )
        avg_tau_expert2 = (kendalltau_df['Expert1 vs Expert2'].mean() )
        avg_tau_expert3 = (kendalltau_df['Expert1 vs Expert3'].mean() )

        # 将平均相关系数添加到矩阵中
        average_results = {
            'Expert1': avg_tau_expert1,
            'Expert2': avg_tau_expert2,
            'Expert3': avg_tau_expert3
        }

      return kendalltau_df, average_results

def calculate_spearman_correlation(df, expert1_scores, expert2_scores, expert3_scores):
    # 计算每个问题（行）三个专家的Spearman's Rank Correlation
    spearman_results = []
    for i in range(len(df)):
        # 获取每个问题的评分
        expert1 = expert1_scores.iloc[i]
        expert2 = expert2_scores.iloc[i]
        expert3 = expert3_scores.iloc[i]

        # 计算专家之间的Spearman相关系数
        corr_12, _ = spearmanr(expert1, expert2)
        corr_13, _ = spearmanr(expert1, expert3)
        corr_23, _ = spearmanr(expert2, expert3)

        # 将每个问题的相关系数存储
        spearman_results.append([corr_12, corr_13, corr_23])

    # 创建结果DataFrame
    spearman_df = pd.DataFrame(spearman_results, columns=[
                               'Expert1 vs Expert2', 'Expert1 vs Expert3', 'Expert2 vs Expert3'])

    # 计算每个专家的平均Spearman相关系数
    avg_corr_expert1 = (spearman_df['Expert1 vs Expert2'].mean() +
                        spearman_df['Expert1 vs Expert3'].mean()) / 2
    avg_corr_expert2 = (spearman_df['Expert1 vs Expert2'].mean() +
                        spearman_df['Expert2 vs Expert3'].mean()) / 2
    avg_corr_expert3 = (spearman_df['Expert1 vs Expert3'].mean() +
                        spearman_df['Expert2 vs Expert3'].mean()) / 2

    # 将平均相关系数添加到矩阵中
    average_results = {
        'Expert1 Average': avg_corr_expert1,
        'Expert2 Average': avg_corr_expert2,
        'Expert3 Average': avg_corr_expert3
    }

    return spearman_df, average_results

# 调用方法并打印结果
kendalltau_df, average_results = calculate_kendalltau(
    df, expert1_scores, expert2_scores, expert3_scores)
print(kendalltau_df)
print("Average Spearman Correlations:")
print(average_results)

# 保存结果到新的Excel文件
kendalltau_df.to_excel('kendalltau_results-tau_a.xlsx', index=False)
