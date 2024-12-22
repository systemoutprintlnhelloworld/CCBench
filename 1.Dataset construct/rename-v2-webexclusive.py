import pandas as pd
import os
import re

# Read the excel file and get the sheet1 as a dataframe
df = pd.read_excel("D:\\研究生\\任务2\\TBS-V2-Web\\TBS-V2-web-ImgAndText.xlsx", sheet_name="Sheet1")


# Get the folder path where the images are stored
folder_path = "D:\\研究生\\任务2\\TBS-V2-Web\\blip"

# Loop through each row of the dataframe
for index, row in df.iterrows():
    # Get the cell value of column B
    cell_value = row[1]

    #如果是空值，跳过
    if pd.isnull(cell_value):
        continue



    # Check if the cell value starts with D:
    if cell_value.startswith("D:"):

        #DEBUG
        print('\n')
        print('旧文件名叫  '+cell_value)
        print('\n')
        # Extract the file name from the cell value using regular expression
        file_name = re.search(r"\\([^\\]+\.jpg)$", cell_value).group(1)
        # Get the old file path by joining the folder path and the file name
        old_file_path = os.path.join(folder_path, file_name)
        # Check if the file exists in the folder
        if os.path.isfile(old_file_path):

           # 将row[0]从float转为字符串
            my_str = str(row[0]) 
        

            #debug
            #换行
            print('\n')
            print('新文件名叫  '+my_str)
            print('\n')

            # Create the new file name based on column A value

            new_file_name = "FIGURE " + my_str  + ".jpg"
            # Get the new file path by joining the folder path and the new file name
            new_file_path = os.path.join(folder_path, new_file_name)
            # Rename the file
            os.rename(old_file_path, new_file_path)
