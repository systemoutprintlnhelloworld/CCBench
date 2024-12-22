import pandas as pd
import numpy as np

# Load the Excel file
file_path = r'd:\研究生\任务3\医生评测结果\open-vqa-汇总(陈医生版).xlsx'
xls = pd.ExcelFile(file_path)

# Load the specific sheet
sheet3_df = pd.read_excel(xls)
# 仅仅读取excel表前三行
# sheet3_df = pd.read_excel(xls, sheet_name='Sheet3', nrows=2)
# print('\033[91m'+'sheet3_df: ' + '\033[92m', sheet3_df)

# Function to calculate MVP counts for the entire sheet


def calculate_mvp_counts(df: pd.DataFrame):
    doctors = ["陈医生", "吴医生", "杨医生"]
    # models = ["GPT-4", "Bard", "Cluade-2", "llama2", "文心一言", "通义千问"]
    models = ["GPT-4-V", "Bard", "llava", "qwen-vl"]


    # Extract relevant 1-16 columns 
    relevant_columns = [col for col in df.columns if any(
        model in col for model in models) and any(doctor in col for doctor in doctors)]
    df_relevant = df[relevant_columns]
    # print('\033[91m'+'df_relevant: ' + '\033[92m', df_relevant)

    # Initialize dictionary to store MVP counts
    mvp_counts = {model: {'one_doctor': 0, 'two_doctors': 0,
                          'three_doctors': 0} for model in models}

    # Calculate MVP counts
    for idx, row in df_relevant.iterrows():
        # Reshape row to a DataFrame with doctors as columns
        # only include 1-12 columns
        reshaped_row = pd.DataFrame(np.reshape( # select 1-12 columns
            row.values, (len(doctors), len(models)), order='F'), columns=models, index=doctors)
            
        # print(reshaped_row)
        # Determine the MVP models for each doctor
        max_scores = reshaped_row.max(axis=1)
        # 需要考虑到多个模型得分相同的情况,此时返回多个模型
        mvp_models_per_doctor = {
            doctor: reshaped_row.loc[doctor][reshaped_row.loc[doctor] == max_scores[doctor]].index.tolist() for doctor in doctors}
        # print(mvp_models_per_doctor)

        # Count MVP occurrences
        mvp_combined = []
        for mvp_models in mvp_models_per_doctor.values():
            mvp_combined.extend(mvp_models)

        unique_models, counts = np.unique(mvp_combined, return_counts=True)
        for model, count in zip(unique_models, counts):
            if count == 1:
                mvp_counts[model]['one_doctor'] += 1
            elif count == 2:
                mvp_counts[model]['two_doctors'] += 1
            elif count == 3:
                mvp_counts[model]['three_doctors'] += 1

    return mvp_counts


# Calculate MVP counts for the entire sheet
mvp_counts_full = calculate_mvp_counts(sheet3_df)

# Convert the result to a DataFrame for better visualization
mvp_counts_full_df = pd.DataFrame(mvp_counts_full).T

# Save the result to a CSV file or display it as needed
mvp_counts_full_df.to_csv('mvp_counts_full-vqa-chen.csv')
# print(mvp_counts_full_df)

# 再计算每个医生评价下各个模型得到的MVP次数
# Function to calculate MVP counts for each doctor


def calculate_mvp_counts_per_doctor(df: pd.DataFrame):
    doctors = ["陈医生", "吴医生", "杨医生"]
    # models = ["GPT-4", "Bard", "Cluade-2", "llama2", "文心一言", "通义千问"]
    models = ["GPT-4-V", "Bard", "llava", "qwen-vl"]


    # Initialize dictionary to store MVP counts
    mvp_counts_per_doctor = {doctor: {model: 0 for model in models}
                             for doctor in doctors}

    # Calculate MVP counts
    for idx, row in df.iterrows():
        # Reshape row to a DataFrame with doctors as columns
        # only include 1-12 columns
        reshaped_row = pd.DataFrame(np.reshape(
            row.values[:12], (len(doctors), len(models)), order='F'), columns=models, index=doctors)
        # Determine the MVP models for each doctor
        max_scores = reshaped_row.max(axis=1)
        mvp_models_per_doctor = {
            doctor: reshaped_row.loc[doctor][reshaped_row.loc[doctor] == max_scores[doctor]].index.tolist() for doctor in doctors}

        # Count MVP occurrences
        for doctor, mvp_models in mvp_models_per_doctor.items():
            for mvp_model in mvp_models:
                mvp_counts_per_doctor[doctor][mvp_model] += 1

    return mvp_counts_per_doctor


count = calculate_mvp_counts_per_doctor(sheet3_df)

# Convert the result to excel
count_df = pd.DataFrame(count)
count_df.to_csv('mvp_counts_per_doctor-vqa-chen.csv')