import requests
load_autodl_token = False
load_autodl_token_info = ''
try:
    from api.user_info import autodl_token
    headers = {"Authorization": autodl_token}
except Exception as e:
    load_autodl_token_info = str(e)
    headers = None
else:
    load_autodl_token = True


def send_notice(title="eg. 来自我的程序", name="eg. 我的ImageNet实验", content="eg. Epoch=100. Acc=90.2"):
    if load_autodl_token:
        resp = requests.post("https://www.autodl.com/api/v1/wechat/message/send",
                            json={
                                "title": title,
                                "name": name,
                                "content": content
                            }, headers=headers)
        return resp


if __name__ == '__main__':
    print(send_notice().content.decode())
