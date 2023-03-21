from enum import Enum
from datetime import datetime
import questionary
from api.bus import Bus
import keyboard
import time
import os
from api.autodl_notice import send_notice
import threading


class ReserveState(Enum):
    START_CAMPUS = 1
    END_CAMPUS = 2
    DATE = 3
    TIME = 4
    CONFIRM = 5
    END = 6
    QUIT = 7


class ReserveBusMenu:
    state = 0
    default_date = datetime.today().strftime("%Y/%m/%d")
    start_campus = ""
    end_campus = ""
    date = ""
    ticket = {}

    def __init__(self, bus: Bus) -> None:
        self.bus = bus
        self.change_state(ReserveState.START_CAMPUS)

    def run(self):
        while self.state != ReserveState.QUIT:
            if self.state == ReserveState.START_CAMPUS:
                is_quit = self.set_start_campus()
                if is_quit:
                    return 1

            elif self.state == ReserveState.END_CAMPUS:
                self.set_end_campus()

            elif self.state == ReserveState.DATE:
                self.set_date()

            elif self.state == ReserveState.TIME:
                self.set_time()

            elif self.state == ReserveState.CONFIRM:
                self.confirm_ticket()

            elif self.state == ReserveState.END:
                self.reserve_ticket()

            elif self.state == ReserveState.QUIT:
                return 0

        return 0

    def change_state(self, state: ReserveState):
        self.state = state

    def set_start_campus(self):
        campus = ["广州国际校区", "大学城校区", "五山校区", "返回主菜单"]
        self.start_campus = questionary.select("请选择起点", choices=campus).ask()

        if self.start_campus != "返回主菜单":
            self.change_state(ReserveState.END_CAMPUS)
            return False
        else:
            return True

    def set_end_campus(self):
        if self.start_campus == "广州国际校区":
            campus = ["大学城校区", "五山校区", "返回"]
        else:
            campus = ["广州国际校区", "返回"]

        self.end_campus = questionary.select("请选择终点", choices=campus).ask()

        if self.end_campus != "返回":
            self.change_state(ReserveState.DATE)
        else:
            self.change_state(ReserveState.START_CAMPUS)

    def set_date(self):
        self.date = questionary.text(
            "请输入查询日期，格式为：yyyy/mm/dd（空字符串则返回）", default=self.default_date
        ).ask()

        if not self.date:
            self.change_state(ReserveState.END_CAMPUS)
        else:
            self.default_date = self.date
            self.change_state(ReserveState.TIME)

    def set_time(self):
        bus_list = self.bus.get_bus_list(self.start_campus, self.end_campus, self.date)
        bus_choices = []

        if len(bus_list) > 0:
            for idx, bus in enumerate(bus_list):
                bus_choices.append(
                    {
                        "name": "{}. {}-{}".format(
                            idx + 1, bus["startDate"], bus["endDate"]
                        ),
                        "value": idx,
                        "disabled": bus["tickets"] == 0,
                    }
                )

            bus_choices.append(
                {"name": "{}. 重选日期".format(len(bus_list) + 1), "value": -1}
            )

            bus_idx = questionary.select(
                "请选择班次（灰色为被预约完的班次）：",
                choices=bus_choices,
                style=questionary.Style(
                    [
                        ("disabled", "#858585 italic"),
                    ]
                ),
            ).ask()

            if bus_idx == -1:
                self.change_state(ReserveState.DATE)
            else:
                print("校巴完整信息：")
                print("IDs: {}".format(bus_list[bus_idx]["ids"]))
                print("日期: {}".format(bus_list[bus_idx]["dateDeparture"]))
                print(
                    "时间: {}-{}".format(
                        bus_list[bus_idx]["startDate"],
                        bus_list[bus_idx]["endDate"],
                    )
                )
                print(
                    "起点-终点: {}-{}".format(
                        bus_list[bus_idx]["startLocation"],
                        bus_list[bus_idx]["downtown"],
                    )
                )

                self.ticket = bus_list[bus_idx]
                self.change_state(ReserveState.CONFIRM)

        else:
            print("{}已经没有校巴了".format(self.date))

            choices = [
                {"name": "是", "value": True},
                {"name": "否", "value": False},
            ]
            is_confirm = questionary.select("是否重选日期", choices=choices).ask()

            if is_confirm:
                self.change_state(ReserveState.DATE)
            else:
                self.change_state(ReserveState.QUIT)

    def confirm_ticket(self):
        choices = [
            {"name": "是", "value": True},
            {"name": "否", "value": False},
        ]
        is_confirm = questionary.select("确认预定", choices=choices).ask()

        if is_confirm:
            self.change_state(ReserveState.END)
        else:
            self.change_state(ReserveState.TIME)

    def reserve_ticket(self):
        tickets = [
            {
                **self.ticket,
                "ischecked": True,
                "subTickets": 1,
            }
        ]

        result = self.bus.reserve_bus(tickets)

        if result["code"] == 200:
            print("预定成功，请到小程序查看二维码上车")
            self.change_state(ReserveState.QUIT)

        else:
            print("预约失败，请重试")
            print("失败信息：{}".format(result["msg"]))
            self.change_state(ReserveState.TIME)


class ListenBus:
    state = 0
    default_date = datetime.today().strftime("%Y/%m/%d")
    start_campus = ""
    end_campus = ""
    date = ""
    ticket = {}
    abort_listen_flag = False

    def __init__(self, bus: Bus) -> None:
        self.bus = bus
        self.change_state(ReserveState.START_CAMPUS)

    def run(self):
        while self.state != ReserveState.QUIT:
            if self.state == ReserveState.START_CAMPUS:
                is_quit = self.set_start_campus()
                if is_quit:
                    return 1

            elif self.state == ReserveState.END_CAMPUS:
                self.set_end_campus()

            elif self.state == ReserveState.DATE:
                self.set_date()

            elif self.state == ReserveState.TIME:
                self.set_time()

            elif self.state == ReserveState.CONFIRM:
                self.confirm_ticket()

            elif self.state == ReserveState.END:
                self.reserve_ticket()

            elif self.state == ReserveState.QUIT:
                return 0

        return 0

    def change_state(self, state: ReserveState):
        self.state = state

    def set_start_campus(self):
        campus = ["广州国际校区", "大学城校区", "五山校区", "返回主菜单"]
        self.start_campus = questionary.select("请选择起点", choices=campus).ask()

        if self.start_campus != "返回主菜单":
            self.change_state(ReserveState.END_CAMPUS)
            return False
        else:
            return True

    def set_end_campus(self):
        if self.start_campus == "广州国际校区":
            campus = ["大学城校区", "五山校区", "返回"]
        else:
            campus = ["广州国际校区", "返回"]

        self.end_campus = questionary.select("请选择终点", choices=campus).ask()

        if self.end_campus != "返回":
            self.change_state(ReserveState.DATE)
        else:
            self.change_state(ReserveState.START_CAMPUS)

    def set_date(self):
        self.date = questionary.text(
            "请输入查询日期，格式为：yyyy/mm/dd（空字符串则返回）", default=self.default_date
        ).ask()

        if not self.date:
            self.change_state(ReserveState.END_CAMPUS)
        else:
            self.default_date = self.date
            self.change_state(ReserveState.TIME)
    
    def listen_keyboard(self):
        while True:
            if keyboard.is_pressed(' '):
                break
        self.abort_listen_flag = True

    def set_time(self):
        self.abort_listen_flag = False
        bus_list_init = self.bus.get_bus_list(self.start_campus, self.end_campus, self.date)
        bus_departure_time = [i["startDate"] for i in bus_list_init][::-1]
        today_bus_dict = dict(zip([i + 1 for i in list(range(len(bus_departure_time)))], bus_departure_time))
        print('以下是可用班次（出发时间）：\n')
        print('编号\t出发时间')
        for key,value in today_bus_dict.items():
            print(key,'\t',value)
        listen_target = input('\n请输入想监听班次的编号（例如：123）：')
        while not (listen_target.isdigit()):
            listen_target = input('输入有误，请重新输入！\n请输入想监听班次的编号（例如：123）：')
        listen_target = [today_bus_dict[int(i)] for i in listen_target if int(i) in today_bus_dict.keys()]
        print('启动监听键盘输入线程...', end='')
        thread = threading.Thread(target=self.listen_keyboard)
        thread.daemon = True
        thread.start()
        print('完成！')
        refresh_time = 5
        
        while True:
            available_bus = list()
            stop = False
            count = 0
            total_available = 0
            bus_list = self.bus.get_bus_list(self.start_campus, self.end_campus, self.date)

            print("\n监听模式 ## ", end='')
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print("当前时间：", current_time)
            print("按空格键退出循环")
            print('余票\t出发地点\t\t到达地点\t出发时间\t到达时间\t日期')
            for item in bus_list:
                if item["startDate"] in listen_target:
                    if int(list(item.values())[-1]) > 0:
                        available_bus.append(item)
                    total_available += int(list(item.values())[-1])
                    print('%s\t%s\t%s\t%s\t\t%s\t\t%s' % tuple(
                        list(item.values())[i] for i in [-1, -3, -2, -5, -4, -6]))
            print('余票：%d 张。' % total_available)
            if total_available > 0:
                send_notice('有票了！！开始预定！')
                self.ticket = available_bus[0]
                self.change_state(ReserveState.END)
                return
            while count < refresh_time:
                print('\r', refresh_time - count, '秒之后再查询')
                time.sleep(1)
                count += 1
                if self.abort_listen_flag:
                    stop = True
                    break
            os.system('cls')
            if stop:
                break
        self.change_state(ReserveState.QUIT)


    def confirm_ticket(self):
        choices = [
            {"name": "是", "value": True},
            {"name": "否", "value": False},
        ]
        is_confirm = questionary.select("确认预定", choices=choices).ask()

        if is_confirm:
            self.change_state(ReserveState.END)
        else:
            self.change_state(ReserveState.TIME)

    def reserve_ticket(self):
        tickets = [
            {
                **self.ticket,
                "ischecked": True,
                "subTickets": 1,
            }
        ]

        result = self.bus.reserve_bus(tickets)

        if result["code"] == 200:
            print("预约成功，请到小程序查看二维码上车")
            send_notice("预约成功！", str(self.ticket), '服务器回复：' + result['msg'])
            self.change_state(ReserveState.QUIT)

        else:
            print("预约失败，请重试")
            send_notice("预约失败！", str(self.ticket), '服务器回复：' + result['msg'])
            self.change_state(ReserveState.TIME)
