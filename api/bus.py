import requests


class Bus:
    def __init__(self, token) -> None:
        user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"

        session = requests.session()
        session.headers["User-Agent"] = user_agent
        session.headers["authorization"] = token
        session.headers["Content-Type"] = "application/json"

        self.session = session
        self.student_id = '2022xxxxxxxx'
        self.student_name = '张三'
        self.base_url = "https://life.gzic.scut.edu.cn/commute/open/commute"
        # proxy = {
        #     'http': 'http://127.0.0.1:7890',
        #     'https': 'http://127.0.0.1:7890'
        # }
        # if not input('你准备用代理吗？输入N不使用代理，其他任意输入为使用代理：').upper() == 'N':
        #     print('正在设置代理...', end='')
        #     self.session.proxies.update(proxy)
        #     print('完成！')

    def list_reserve(self, status=0, page_num=1, page_size=8):
        url = "{}/commuteOrder/orderFindAll?status={}&PageNum={}&PageSize={}".format(
            self.base_url, status, page_num, page_size
        )

        result = self.session.get(url).json()

        return result

    def ticket_detail(self, ticket_id):
        url = "{}/commuteOrder/ticketDetail?id={}".format(self.base_url, ticket_id)

        result = self.session.get(url).json()

        return result

    def cancel_ticket(self, ticket_id):
        url = "{}/commuteOrder/cancelTicket?id={}".format(self.base_url, ticket_id)

        result = self.session.get(url).json()

        return result

    def delete_ticket(self, ticket_id):
        url = "{}/commuteOrder/removeOrderCanal?id={}".format(self.base_url, ticket_id)

        result = self.session.get(url).json()

        return result

    def get_bus_list(self, start_campus, end_campus, date):
        url = self.base_url + "/commuteOrder/frequencyChoice?PageNum=0&PageSize=0"

        data = {
            "startDate": date,
            "startCampus": start_campus,
            "endDate": date,
            "endCampus": end_campus,
            "startHsTime": "00:00",
            "endHsTime": "23:59",
        }

        result = self.session.post(url, json=data).json()

        return result["list"]

    def reserve_bus(self, tickets):
        url = self.base_url + "/commuteOrder/submitTicket"

        result = self.session.post(url, json=tickets).json()

        return result

    def qrcode_data(self, ticket_id):
        result = self.ticket_detail(ticket_id)["data"]

        return {"id": result["id"], "frequencyId": result["frequencyId"]}
    
    def get_user_info(self):
        res = self.session.get('https://life.gzic.scut.edu.cn/auth/info').json()['data']
        self.student_id = res['account']
        self.student_name = res['nickname']
    
    def show_user_info(self):
        print('当前用户：%s（学号：%s）' % (self.student_name, self.student_id))
