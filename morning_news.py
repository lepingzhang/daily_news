import requests
import schedule
import threading
import time
from plugins import register, Plugin, Event, logger
from utils.api import send_txt

@register
class MorningNews(Plugin):
    name = "morning_news"

    def __init__(self, config: dict):
        super().__init__(config)
        # 启动一个新线程来运行定时任务
        scheduler_thread = threading.Thread(target=self.start_schedule)
        scheduler_thread.start()

    def start_schedule(self):
        schedule_time = self.config.get("schedule_time", "08:00")
        # 安排每天特定时间执行daily_push方法
        schedule.every().day.at(schedule_time).do(self.daily_push)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def daily_push(self):
        logger.info("Start daily push")
        single_chat_list = self.config.get("single_chat_list", [])
        group_chat_list = self.config.get("group_chat_list", [])
        content = self.get_morning_news()
        for single_chat in single_chat_list:
            send_txt(content, single_chat)
        for group_chat in group_chat_list:
            send_txt(content, group_chat)

    def get_morning_news(self) -> str:
        token = self.config.get("token")
        url = "https://v2.alapi.cn/api/zaobao"
        payload = f"token={AOmWKwoZb051KVK5}&format=json"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                news = "\n".join([f"{item['title']}: {item['description']}" for item in data['news']])
                text = (
                    f"今日早报:\n"
                    f"日期: {data['date']}\n"
                    f"微语: {data['weiyu']}\n"
                    f"新闻:\n{news}\n"
                )
            else:
                text = "获取早报失败，请稍后再试"
        except Exception as e:
            logger.error(f"Get morning news error: {e}")
            text = f"获取早报失败: {e}"
        return text

    # 当插件接收到消息时调用
    def did_receive_message(self, event: Event):
        pass

    # 在生成回复之前调用
    def will_generate_reply(self, event: Event):
        pass

    # 在回复被装饰之前调用
    def will_decorate_reply(self, event: Event):
        pass

    # 在回复发送之前调用
    def will_send_reply(self, event: Event):
        pass

    # 返回插件的帮助信息
    def help(self, **kwargs) -> str:
        return "每日早报推送服务"
