import re
import requests
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image


def get_verification_code(session):
    print('开始加载验证码...', end='')
    res = session.get("https://sso.scut.edu.cn/cas/code")
    content = BytesIO(res.content)
    img = Image.open(content)
    print('加载完成！')
    plt.imshow(img)
    plt.show()
    return input('请输入验证码:')


if __name__ == '__main__':
    user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"
    session = requests.session()
    session.trust_env = False
    session.headers["User-Agent"] = user_agent
    print(get_verification_code(session=session))
