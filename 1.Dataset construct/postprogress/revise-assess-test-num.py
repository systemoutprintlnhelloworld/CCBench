# 顺序读取 D:\研究生\任务3\医生评测结果\吴医生结果\open-vqa网页模板-离线版 路径下的html文件,直到其中文件名与上一个文件名差值大于1时停止
# 最后打印当前文件名
import os

# 读取路径
path = r'D:\研究生\任务3\医生评测结果\吴医生结果\网页模板-离线版(1)\网页模板-离线版(1)\open-qa网页模板-离线版\评分'
# 读取路径下的所有文件名
file_list = os.listdir(path)
# 分割文件名,取出文件名中的数字部分
file_list = [int(file.split('.')[0]) for file in file_list if file.endswith('.mhtml')]

# 首先找到当前目录中1.html的文件,接着找2.html,3.html,4.html,以此类推,直到找不到i+1.html时停止
for   i in range(1, len(file_list)+1):
    if i not in file_list:
      print("未找到文件"+ str(i+1)+".html")
      break