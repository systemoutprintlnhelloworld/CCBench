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
        worksheet = workbook['Sheet1']
        image_dict = dict()
        for cell in worksheet['A']:
            if cell.hyperlink:
                img_url = cell.hyperlink.target
                img_name = os.path.basename(img_url)
                if img_name.endswith('jpg'):  # select jpg
                    img_name = unquote(img_name)
                    image_dict[img_name] = img_url
                else:
                    print(cell, img_url)

        self.img_dict = image_dict

    def write(self):
      #当下载中遇到问题，报错并跳过，继续下载
      try:
          for key, value in tqdm(self.img_dict.items()):
            savePath = os.path.join(self.dst, key)

            mysite_request = Request(value, headers=self.headers) #{"User-Agent": "Mozilla/5.0"}
            response = urlopen(mysite_request)
            img = response.read()
            with open(savePath, 'wb') as f:
                f.write(img)
                f.close()
      except Exception as e:
              print(e)
              pass  
      
            


if __name__ == '__main__':
    src = r"D:\\E盘迁移文件\\研究生-科研\\任务2\\TBS-web\\V3\\V3.xlsx"
    dst = r'D:\\E盘迁移文件\\研究生-科研\\任务2\\TBS-web\\V3\\PNG'
    download = Download(src, dst)
    download.write()













