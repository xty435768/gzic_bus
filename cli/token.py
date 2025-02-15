import questionary
import os.path as path
from api.get_token import check_token_expired, get_token

TOKEN_PATH = ".token"


def load_token(
        username=None, password=None
        ):
    token = ""
    print("读取token文件中...")

    if path.exists(TOKEN_PATH):
        with open(TOKEN_PATH) as f:
            token = f.read().strip()

            if check_token_expired(token):
                print("token过期")
                login(username, password)
            else:
                print("token读取成功")
    else:
        token = login(username, password)

    return token


def login(username=None, password=None):
    if not username or not password:
        print("请先使用统一认证账号登陆获取token")
        # username = questionary.text("学号：").ask()
        # password = questionary.password("密码：").ask()
        username = input('学号：')
        password = input('密码：')

    if not username or not password:
        print("请输入用户名和密码")
        exit()

    token = get_token(username, password)
    print("登录成功! token为", token)
    print("现在保存token文件...", end='')

    with open(TOKEN_PATH, "w+") as f:
        f.write(token)
    print("保存完成")
    return token
