import pandas as pd
import numpy as np

# import excel
data = pd.read_excel(
    r'D:\研究生\任务3\医生评测结果\open-vqa-汇总(陈医生版).xlsx', sheet_name='Sheet1')
# Assuming data is already loaded into variables: rao_ratings, wu_ratings, yang_ratings
# Define the relevant columns for each doctor
rao_columns = [
    'GPT-4-V-陈医生\t\t\t', 'Bard-陈医生\t\t\t', 'llava-陈医生\t\t\t', 'qwen-vl-陈医生\t\t\t'
]
wu_columns = [
    'GPT-4-V-吴医生\t\t\t', 'Bard-吴医生\t\t\t', 'llava-吴医生\t\t\t', 'qwen-vl-吴医生\t\t\t'
]
yang_columns = [
    'GPT-4-V-杨医生\t\t\t\t\t', 'Bard-杨医生\t\t\t\t\t', 'llava-杨医生\t\t\t\t\t', 'qwen-vl-杨医生\t\t\t\t\t'
]


# Extract relevant columns
rao_ratings = data[rao_columns]
wu_ratings = data[wu_columns]
yang_ratings = data[yang_columns]

# Convert to numeric, handling non-numeric values
rao_ratings = rao_ratings.apply(pd.to_numeric, errors='coerce')
wu_ratings = wu_ratings.apply(pd.to_numeric, errors='coerce')
yang_ratings = yang_ratings.apply(pd.to_numeric, errors='coerce')

# Determine top-rated models for each doctor
rao_top_rated = rao_ratings.idxmax(axis=1)
wu_top_rated = wu_ratings.idxmax(axis=1)
yang_top_rated = yang_ratings.idxmax(axis=1)

# Remove trailing characters after the hyphen and any whitespace in the dataframe
rao_top_rated = rao_top_rated.str.replace(r'-.*\s*', '', regex=True)
wu_top_rated = wu_top_rated.str.replace(r'-.*\s*', '', regex=True)
yang_top_rated = yang_top_rated.str.replace(r'-.*\s*', '', regex=True)
# Combine the top-rated data
top_rated_combined = pd.DataFrame({
    '陈医生': rao_top_rated,
    '吴医生': wu_top_rated,
    '杨医生': yang_top_rated
})

# Initialize the confusion matrix
doctors = ['陈医生', '吴医生', '杨医生']
n_doctors = len(doctors)
confusion_matrix = np.zeros((n_doctors, n_doctors))

# Compare the top-rated models and fill the confusion matrix
for idx in range(top_rated_combined.shape[0]):
    for i in range(n_doctors):
        for j in range(n_doctors):
            if top_rated_combined.iloc[idx, i] == top_rated_combined.iloc[idx, j]:
                confusion_matrix[i, j] += 1

# Normalize the confusion matrix by the number of questions
confusion_matrix /= top_rated_combined.shape[0]

# Convert the confusion matrix to a DataFrame for easier manipulation and saving
confusion_df = pd.DataFrame(confusion_matrix, index=doctors, columns=doctors)

# Save the confusion matrix to an Excel file
output_path = 'doctor_agreement_confusion_matrix-chen_vqa.xlsx'
confusion_df.to_excel(output_path)
