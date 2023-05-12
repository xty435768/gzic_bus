import re
import requests
from api.des import str_enc
from api.get_verification_code import get_verification_code


# 为新的统一认证系统（新增华工企业号二次验证码）做的登录，当前life.gzic.scut.edu.cn尚未接入该系统，故暂时弃用
def scut_sso(username: str, password: str):
    # A fake user agent
    user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"

    session = requests.session()
    session.trust_env = False
    session.headers["User-Agent"] = user_agent

    # This will be rediect to the login page
    redirect_login_page = session.get("https://life.gzic.scut.edu.cn/")
    verification_code = get_verification_code(session)
    lt_pattern = re.compile(r'<input.+name="lt"\s+value="([^"]+)"')
    lt = re.search(lt_pattern, redirect_login_page.text).group(1)

    login_post_param = {
        "code": str(verification_code),
        "ul": len(username),
        "pl": len(password),
        "lt": lt,
        "rsa": str_enc(username + password + lt, "1", "2", "3"),
        "execution": "e1s1",
        "_eventId": "submit",
    }

    # 第一次提交登录请求
    res = session.post(
        url="https://sso.scut.edu.cn/cas/login?service=https%3A%2F%2Flife.gzic.scut.edu.cn%2Flogin%2Fcas%2F",
        data=login_post_param)
    # 再get一次触发二次验证码下发
    res = session.get(url="https://sso.scut.edu.cn/cas/login")
    # print(res.text)
    pm1 = input('请输入二次认证验证码,有效期90秒。请通过微信企业号华南理工大学的消息通知或手机短信查收: ')
    login_PM_post_param = {
        'PM1': pm1,
        "ul": "",
        "pl": "",
        "lt": lt,
        "rsa": "",
        'execution': 'e1s2',
        '_eventId': 'submit'
    }
    # 第二次提交登录请求
    res = session.post(url="https://sso.scut.edu.cn/cas/login?service=https%3A%2F%2Fmy.scut.edu.cn%2Fup%2F",
                       data=login_PM_post_param)

    return session, res


def get_token(username: str, password: str):
    session, res = scut_sso(username, password)
    token = session.get("https://life.gzic.scut.edu.cn/auth/login/cas/token").json()
    return token["data"]


def check_token_expired(token):
    user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"

    session = requests.session()
    session.trust_env = False
    session.headers["User-Agent"] = user_agent
    session.headers["authorization"] = token

    result = session.get(
        "https://life.gzic.scut.edu.cn/commute/open/commute/commuteOrder/orderFindAll?status=0&PageNum=1&PageSize=1"
    ).json()

    return result["code"] != 200


if __name__ == "__main__":
    from user_info import username, password

    session, res = scut_sso(username, password)
    print(res.text)
    res_test = session.post(url='https://my.scut.edu.cn/up/sys/uacm/profile/getUserById', data={
        "ID_NUMBER": username
    })
    print(res_test.text)
