# 导入所需的模块
#为每个代码在其上提供注释
import openpyxl
import os
from urllib.request import Request, urlopen
from urllib.parse import unquote
from tqdm import tqdm

class Download():
    def __init__(self, excel_root, dst):
        self.src = excel_root
        self.dst = dst
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        self.read_url()
    def read_url(self):
        workbook = openpyxl.load_workbook(self.src)
        worksheet = workbook['Sheet2'] 
        image_dict = dict()

        # 读取第一行的单元格，获取图片的名称
        order_numbers = [cell.value for cell in worksheet['A1':'MB1'][0]]
        
  
        # 读取第二行的单元格，获取图片的链接
        links_inner = [cell.value if cell.value else None for cell in worksheet['A3':'MB3'][0]]


        # 遍历两个列表，生成图片的名称和链接的字典
        for order_number, link in zip(order_numbers, links_inner):


            # DEBUG
            print(order_number, link)
            
            # 判断链接是否为空或者是本地文件链接
            if link is None or link.startswith("D:\\"):
                # 跳过这一对，继续下一对
                continue
            # 判断链接是否是网页链接（以https开头）
            elif link.startswith("https"):
                # 需要修改link中的文本，将其从形如“https://web.archive.org/web/20150905104549im_http://nih.techriver.net/patientImages/1099.jpg” 中间的im_http 段改成im_/http
                link = link.replace("im_http", "im_/http")
                # 从链接中提取图片的扩展名（如.jpg）
                ext = os.path.splitext(link)[1]
                
                # 拼接图片的完整名称（如FIGURE 1.1.jpg）
            
                image_name = f"{order_number}{ext}"
                # 将图片的名称和链接添加到字典中
                image_dict[image_name] = link
            else:
                # 打印无效链接的信息
                print(f"无效链接：{link}")

        self.img_dict = image_dict

    def write(self):
      #当下载中遇到问题，报错并跳过，继续下载
      try:
          # 使用tqdm模块创建一个进度条对象
          pbar = tqdm(self.img_dict.items())
          for key, value in pbar:
            savePath = os.path.join(self.dst, key)

            mysite_request = Request(value, headers=self.headers) #{"User-Agent": "Mozilla/5.0"}
            response = urlopen(mysite_request)
            img = response.read()
            with open(savePath, 'wb') as f:
                f.write(img)
                f.close()
            # 更新进度条的描述信息，显示文件名
            pbar.set_description(f"下载成功：{key}")
      except Exception as e:
              print(e)
              pass  
      
            


if __name__ == '__main__':
    src = r"D:\\E盘迁移文件\\研究生-科研\\任务2\\TBS-V2-Web\\TBS-V2-web-ImgAndText.xlsx"
    dst = r'D:\\E盘迁移文件\\研究生-科研\\任务2\\TBS-web-独有\\V2'
    download = Download(src, dst)
    download.write()
