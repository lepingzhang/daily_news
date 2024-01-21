import requests
import schedule
import threading
import time
from plugins import register, Plugin, Event, logger
from utils.api import send_txt

@register
class DailyNews(Plugin):
    name = "daily_news"

    def __init__(self, config: dict):
        super().__init__(config)
        scheduler_thread = threading.Thread(target=self.start_schedule)
        scheduler_thread.start()

    def did_receive_message(self, event: Event):
        # 当收到特定命令时发送早报
        command = self.config.get("command")
        if event.message == command:
            content = self.get_daily_news()
            send_txt(content, event.sender_id)

    def will_generate_reply(self, event: Event):
        pass

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "每日早报"

    def start_schedule(self):
        schedule_time = self.config.get("schedule_time", "08:00")
        schedule.every().day.at(schedule_time).do(self.daily_push)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def daily_push(self):
        logger.info("Start daily push")
        single_chat_list = self.config.get("single_chat_list", [])
        group_chat_list = self.config.get("group_chat_list", [])
        content = self.get_daily_news()
        for single_chat in single_chat_list:
            send_txt(content, single_chat)
        for group_chat in group_chat_list:
            send_txt(content, group_chat)

    def get_daily_news(self) -> str:
        try:
            url = "https://v2.alapi.cn/api/zaobao"
            token = self.config.get("token")  # 从配置中动态获取token
            payload = f"token={token}&format=json"
            headers = {'Content-Type': "application/x-www-form-urlencoded"}

            response = requests.request("POST", url, data=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # 根据早报的数据结构来格式化消息文本
                text = f"今日早报:\n{data['content']}"  # 假设早报内容在返回数据的'content'字段中
            else:
                text = "获取早报失败, 请稍后再试"
        except Exception as e:
            logger.error(f"Get daily news error: {e}")
            text = f"获取早报失败: {e}"
        return text
