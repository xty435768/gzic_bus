import re
import requests
from io import BytesIO
# import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def ascill_art(file: Image):
    im = file
    sample_rate = 0.75
    aspect_ratio = 0.75
    new_im_size = np.array(
        [im.size[0] * sample_rate, im.size[1] * sample_rate * aspect_ratio]
    ).astype(int)
    im = im.resize(new_im_size)
    im = np.array(im)
    symbols = np.array(list(" .-vM"))
    im = (im - im.min()) / (im.max() - im.min()) * (symbols.size - 1)
    ascii = symbols[im.astype(int)]
    for r in ascii:
        line = "".join(r)
        if line == len(line) * line[0]:
            continue
        print(line)

def get_verification_code(session):
    print('开始加载验证码...', end='')
    res = session.get("https://sso.scut.edu.cn/cas/code")
    content = BytesIO(res.content)
    img = Image.open(content)
    print('加载完成！')
    ascill_art(img)
    # plt.imshow(img)
    # plt.show()
    # img.save('code.jpg')
    # print('验证码已保存为code.jpg。如果无法打开绘图窗口（例如在SSH环境中）请查看该图片文件！')
    return input('请输入验证码:')


if __name__ == '__main__':
    user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"
    session = requests.session()
    session.trust_env = False
    session.headers["User-Agent"] = user_agent
    print(get_verification_code(session=session))
