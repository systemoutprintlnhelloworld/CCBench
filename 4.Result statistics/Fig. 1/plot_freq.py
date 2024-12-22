import re
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

# 更新医学术语列表，包含TBS标准的宫颈病理学相关单词
medical_terms = [
    'cell', 'nucleus', 'cytoplasm', 'mitosis', 'apoptosis', 'membrane',
    'organelle', 'chromosome', 'gene', 'DNA', 'RNA', 'protein', 'enzyme',
    'endocervical', 'squamous', 'atypical', 'adenocarcinoma', 'endometrial',
    'cytoplasmic', 'cytoplasm', 'chromatin', 'carcinoma', 'nucleoli',
    'cytology', 'cytological', 'endocervix', 'endometrium', 'pathology',
    'biopsy', 'lesion', 'malignant', 'benign', 'metastasis', 'histology',
    'immunohistochemistry', 'cytochemistry', 'oncology', 'hematology',
    'lymphoma', 'leukemia', 'melanoma', 'sarcoma', 'neoplasm', 'tumor',
    'inflammation', 'hyperplasia', 'dysplasia', 'necrosis', 'fibrosis',
    'ulcer', 'hemorrhage', 'thrombosis', 'embolism', 'infection',
    'bacteria', 'virus', 'fungus', 'parasite', 'antibody', 'antigen',
    'vaccine', 'chemotherapy', 'radiotherapy', 'surgery', 'diagnosis',
    'prognosis', 'treatment', 'therapy', 'syndrome', 'disease', 'disorder',
    # TBS标准相关术语
    'ASCUS', 'LSIL', 'HSIL', 'AGC', 'NILM', 'CIN1', 'CIN2', 'CIN3',
    'HPV', 'Koilocytosis', 'Parakeratosis', 'Hyperkeratosis', 'Metaplasia',
    'Dyskeratosis', 'Polymorphonuclear', 'Endometritis', 'Follicular',
    'Histopathology', 'Microbiopsy', 'Colposcopy', 'Cytobrush', 'Endocervical',
    'Ectocervical', 'Transformation zone', 'Squamous metaplasia', 'Atypia',
    'Koilocyte', 'Nucleomegaly', 'Hyperchromasia', 'Mitoses', 'Maturation',
    'Reactive', 'Inflammatory', 'Atrophic', 'Microinvasive', 'Invasive',
    'Keratinizing', 'Nonkeratinizing', 'Basal cells', 'Parabasal cells',
    'Superficial cells', 'Intermediate cells', 'Endocervical cells',
    'Columnar cells', 'Reserve cells', 'Squamous cells', 'Glandular cells'
]

# 英文停用词
stop_words = set(stopwords.words('english'))

if __name__ == '__main__':
    print('ohno')
    # 读取数据集
    is_vqa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\is_vqa.xlsx')
    open_vqa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\open_vqa.xlsx')
    is_qa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\is_qa.xlsx')
    open_qa = pd.read_excel(r'D:\研究生\任务3\代码\统计-题库\open_qa.xlsx')

    # 计算问题的句子长度
    is_vqa['question_length'] = is_vqa['questions'].apply(
        lambda x: len(str(x).split()))
    open_vqa['question_length'] = open_vqa['question'].apply(
        lambda x: len(str(x).split()))
    is_qa['question_length'] = is_qa['qustion'].apply(
        lambda x: len(str(x).split()))
    open_qa['question_length'] = open_qa['qustion'].apply(
        lambda x: len(str(x).split()))

    # 计算答案的句子长度 (open_vqa 和 open_qa)
    open_vqa['answer_length'] = open_vqa['answer'].apply(
        lambda x: len(str(x).split()))
    open_qa['answer_length'] = open_qa['answer'].apply(
        lambda x: len(str(x).split()))

    # 合并结果到一个数据框中用于频率分布
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

    # 频率分布
    frequency_distribution_df = question_lengths.groupby(
        ['length', 'type']).size().unstack(fill_value=0)

    # 保存频率分布到 Excel
    output_path = r'D:\研究生\任务3\代码\统计-题库\frequency_distribution.xlsx'
    frequency_distribution_df.to_excel(output_path)

    # 单词频率统计
    def count_medical_words(text, terms, stop_words):
        words = re.findall(r'\b\w+\b', str(text).lower())
        # 将terms中单词变为小写
        terms = [term.lower() for term in terms]
        relevant_words = [
            word for word in words if word in terms and word not in stop_words]
        return Counter(relevant_words)

    def count_terms_in_dataframe(df, question_col, answer_col=None):
        term_counts = Counter()
        df[question_col].apply(lambda x: term_counts.update(
            count_medical_words(x, medical_terms, stop_words)))
        if answer_col:
            df[answer_col].apply(lambda x: term_counts.update(
                count_medical_words(x, medical_terms, stop_words)))
        return term_counts

    # 汇总所有数据集中的单词计数
    question_counts = Counter()
    answer_counts = Counter()
    question_counts.update(count_terms_in_dataframe(is_vqa, 'questions'))
    answer_counts.update(count_terms_in_dataframe(
        open_vqa, 'question', 'answer'))
    question_counts.update(count_terms_in_dataframe(is_qa, 'qustion'))
    answer_counts.update(count_terms_in_dataframe(
        open_qa, 'qustion', 'answer'))

    # 合并计数结果并准备绘图
    combined_counts = Counter()
    combined_counts.update(question_counts)
    combined_counts.update(answer_counts)

    # 过滤掉频率低于50的单词
    filtered_combined_counts = {term: freq for term,
                                freq in combined_counts.items() if freq >= 50}

    # 获取前50个最常见的医学术语
    most_common_questions = question_counts.most_common(50)
    most_common_answers = answer_counts.most_common(50)
    most_common_combined = combined_counts.most_common(50)

    question_df = pd.DataFrame(most_common_questions, columns=[
                               'Term', 'Question_Frequency'])
    answer_df = pd.DataFrame(most_common_answers, columns=[
                             'Term', 'Answer_Frequency'])
    combined_df = pd.merge(question_df, answer_df,
                           on='Term', how='outer').fillna(0)
    combined_df['Total_Frequency'] = combined_df['Question_Frequency'] + \
        combined_df['Answer_Frequency']

    # 按总频率排序
    combined_df = combined_df.sort_values(
        by='Total_Frequency', ascending=False)

    # 绘制单词频率分布图
    plt.figure(figsize=(12, 8))
    plt.barh(combined_df['Term'], combined_df['Question_Frequency'],
             color='skyblue', label='Question')
    plt.barh(combined_df['Term'], combined_df['Answer_Frequency'],
             left=combined_df['Question_Frequency'], color='lightcoral', label='Answer')
    plt.xlabel('Frequency')
    plt.ylabel('Terms')
    plt.title(
        f'Top {len(most_common_questions)} Most Frequent Medical Terms')  # 动态标题
    plt.gca().invert_yaxis()  # 反转y轴以显示最频繁的术语在顶部
    # plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    # 边框设置为0.5
    plt.gca().spines['top'].set_linewidth(0.5)
    # 长宽比改为`1:2`
    plt.gca().set_aspect('auto', adjustable='box')
    # 边框设置为0.5
    plt.gca().spines['left'].set_linewidth(0.5)
    plt.legend()
    # 图例位于右下角
    plt.legend(loc='lower right')
    plt.rcParams['svg.fonttype'] = 'none'
    # plt.show()
    # 保存图表为SVG格式
    plt.savefig(
        r'D:\研究生\任务3\代码\统计-题库\medical_term_frequency_distribution.svg', format='svg')
# 保存数据到excel表
    combined_df.to_excel(
        r'D:\研究生\任务3\代码\统计-题库\medical_term_frequency_distribution.xlsx')
    print("图表已保存为 SVG 格式。")
