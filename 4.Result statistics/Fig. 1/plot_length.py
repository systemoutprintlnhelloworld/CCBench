import re
import pandas as pd
from collections import Counter

if __name__ == 'main':
    print('ohno')
    # Load the datasets
    is_vqa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\is_vqa.xlsx')
    open_vqa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\open_vqa.xlsx')
    is_qa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\is_qa.xlsx')
    open_qa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\open_qa.xlsx')

    # Calculate sentence length for questions
    is_vqa['question_length'] = is_vqa['questions'].apply(
        lambda x: len(str(x).split()))
    open_vqa['question_length'] = open_vqa['question'].apply(
        lambda x: len(str(x).split()))
    is_qa['question_length'] = is_qa['qustion'].apply(
        lambda x: len(str(x).split()))
    open_qa['question_length'] = open_qa['qustion'].apply(
        lambda x: len(str(x).split()))

    # Calculate sentence length for answers in open_vqa and open_qa
    open_vqa['answer_length'] = open_vqa['answer'].apply(
        lambda x: len(str(x).split()))
    open_qa['answer_length'] = open_qa['answer'].apply(
        lambda x: len(str(x).split()))

    # Combine results into a single dataframe for frequency distribution
    question_lengths = pd.concat([
        is_vqa[['question_length']].rename(
            columns={'question_length': 'length'}).assign(type='is_vqa_question'),
        open_vqa[['question_length']].rename(
            columns={'question_length': 'length'}).assign(type='open_vqa_question'),
        is_qa[['question_length']].rename(
            columns={'question_length': 'length'}).assign(type='is_qa_question'),
        open_qa[['question_length']].rename(
            columns={'question_length': 'length'}).assign(type='open_qa_question'),
        open_vqa[['answer_length']].rename(
            columns={'answer_length': 'length'}).assign(type='open_vqa_answer'),
        open_qa[['answer_length']].rename(
            columns={'answer_length': 'length'}).assign(type='open_qa_answer')
    ])

    # Frequency distribution
    frequency_distribution_df = question_lengths.groupby(
        ['length', 'type']).size().unstack(fill_value=0)

    # Save frequency distribution to Excel
    output_path = r'D:\研究生\任务3\代码\统计-题库\frequency_distribution.xlsx'
    frequency_distribution_df.to_excel(output_path)

if __name__ != 'main':
    import pandas as pd
    import matplotlib.pyplot as plt

    # Load the frequency distribution data
    frequency_distribution_df = pd.read_excel(
        r'D:\研究生\任务3\代码\统计-题库\frequency_distribution.xlsx')

    # Filter the data for plotting
    question_data = frequency_distribution_df.filter(like='question', axis=1)
    answer_data = frequency_distribution_df.filter(like='answer', axis=1)

    # Set font to Times New Roman
    plt.rcParams["font.family"] = "Times New Roman"

    # Plotting the question length distribution
    plt.figure(figsize=(10, 6))
    for column in question_data.columns:
        plt.bar(question_data.index,
                question_data[column], alpha=0.5, label=column)

    plt.xlim(0, 38)  # Set x-axis limit
    plt.ylim(0)  # Ensure y-axis starts from 0
    plt.xlabel('Question Length (in number of words)')
    plt.ylabel('Number of Questions')
    plt.title('Question Length Distribution')

    # Add major and minor ticks
    plt.xticks(range(0, 39, 5))
    plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(2.5))
    # plt.yticks(range(0, int(question_data.max().max() + 1), 100))
    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(50))

    # Add grid for both major and minor ticks
    # plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    # 边框设置为0.5
    plt.gca().spines['bottom'].set_linewidth(0.5)
    plt.legend()
    # plt.show()
    # 保存为svg格式
    plt.savefig(r'D:\研究生\任务3\代码\统计-题库\question_length_distribution.svg')

    # Plotting the answer length distribution
    plt.figure(figsize=(10, 6))
    for column in answer_data.columns:
        # Shift the bars to the right by 1
        plt.bar(answer_data.index + 1,
                answer_data[column], alpha=0.5, label=column)

    plt.xlim(0, answer_data.index.max() + 2)  # Adjust x-axis to fit the data
    plt.ylim(0)  # Ensure y-axis starts from 0
    plt.xlabel('Answer Length (in number of words)')
    plt.ylabel('Number of Answers')
    plt.title('Answer Length Distribution')

    # Add major and minor ticks
    plt.xticks(range(0, int(answer_data.index.max() + 2), 5))
    plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(2.5))
    # plt.yticks(range(0, int(answer_data.max().max() + 1), 100))
    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(50))

    # Add grid for both major and minor ticks
    # plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    # 边框设置为0.5
    plt.gca().spines['bottom'].set_linewidth(0.5)
    plt.legend()
    # plt.show()
    # 保存为svg格式
    plt.savefig(r'D:\研究生\任务3\代码\统计-题库\answer_length_distribution.svg')
    # Load the datasets
    is_vqa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\is_vqa.xlsx')
    open_vqa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\open_vqa.xlsx')
    is_qa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\is_qa.xlsx')
    open_qa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\open_qa.xlsx')
    
    # 保存answer_length_distribution到excel
    answer_length_distribution = pd.DataFrame(answer_data.sum(axis=1), columns=['count'])
    answer_length_distribution.to_excel(r'D:\研究生\任务3\代码\统计-题库\answer_length_distribution.xlsx')
   