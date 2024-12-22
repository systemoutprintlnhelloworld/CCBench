# User agent example

from urllib import request

from urllib.request import Request, urlopen


# store website address in a variable

website_url = "https://bethesda.soc.wisc.edu/atlasimages/fig%201.2.jpg"


# Providing user agent information

mysite_request = Request(website_url, headers={"User-Agent": "Mozilla/5.0"})

# Open the website url
response = urlopen(mysite_request)

# 读取图片
img = response.read()

#文件名设置为website_url 的最后一部分
filename = website_url.split('/')[-1]

#debug
print(filename)

# 保存到本地"D:\研究生\任务2\img"文件夹下
with open(r"D:\\研究生\\任务2\\img\\"+filename, 'wb') as f:
    f.write(img)
    f.close()

# 打印提示信息
print("图片下载成功！")

from PIL import Image, ImageChops

# 读取图片并转换为灰度
im1 = Image.open("D:\\研究生\\任务2\\img\\微信图片_20230707185445.png").convert("L")
im2 = Image.open("D:\\研究生\\任务2\\img\\"+filename).convert("L")

# 计算两个图片的差异
diff = ImageChops.difference(im1, im2)

# 如果两个图片完全相同，差异为0
if diff.getbbox() is None:
    print("两个图片一样")
else:
    print("两个图片不一样")




