import requests
import schedule
import threading
import time
from plugins import register, Plugin, Event, logger, Reply, ReplyType
from utils.api import send_txt

def send_img(image_url, target):
    # 实现发送图片的逻辑
    print(f"Sending image to {target}: {image_url}")
    # 这里添加发送图片的代码

class Reply:
    def __init__(self, reply_type, content):
        self.type = reply_type
        self.content = content  # 文本内容或图片URL存储在这里

@register
class DailyNews(Plugin):
    name = "daily_news"
    zaobao_api_url = "https://v2.alapi.cn/api/zaobao"

    def __init__(self, config):
        super().__init__(config)
        scheduler_thread = threading.Thread(target=self.start_schedule)
        scheduler_thread.start()

    def will_generate_reply(self, event: Event):
        query = event.message.content.strip()
        commands = self.config.get("command", [])
        if any(cmd in query for cmd in commands):
            replies = self.get_daily_news()
            if isinstance(replies, list):
                for reply in replies:
                    # 使用 event.channel.send 发送回复
                    event.channel.send(reply, event.message)
            else:
                # 使用 event.channel.send 发送回复
                event.channel.send(replies, event.message)
            event.bypass()

    def start_schedule(self):
        schedule_time = self.config.get("schedule_time", "09:00")
        schedule.every().day.at(schedule_time).do(self.daily_push)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def daily_push(self):
        logger.info("开始每日推送")
        single_chat_list = self.config.get("single_chat_list", [])
        group_chat_list = self.config.get("group_chat_list", [])
        replies = self.get_daily_news()
        if isinstance(replies, list):  # 如果返回的是列表，我们假设列表中有多个回复对象
            for reply in replies:
                for single_chat in single_chat_list:
                    if reply.type == ReplyType.TEXT:
                        send_txt(reply.content, single_chat)  # 假设send_txt方法接收内容和接收者ID
                    elif reply.type == ReplyType.IMAGE:
                        send_img(reply.content, single_chat)  # 假设send_img方法接收图片URL和接收者ID
                for group_chat in group_chat_list:
                    if reply.type == ReplyType.TEXT:
                        send_txt(reply.content, group_chat)  # 假设send_txt方法接收内容和接收者ID
                    elif reply.type == ReplyType.IMAGE:
                        send_img(reply.content, group_chat)  # 假设send_img方法接收图片URL和接收者ID
        elif replies:  # 如果返回的不是列表，我们直接发送
            for single_chat in single_chat_list:
                if replies.type == ReplyType.TEXT:
                    send_txt(replies.content, single_chat)  # 假设send_txt方法接收内容和接收者ID
                elif replies.type == ReplyType.IMAGE:
                    send_img(replies.content, single_chat)  # 假设send_img方法接收图片URL和接收者ID
            for group_chat in group_chat_list:
                if replies.type == ReplyType.TEXT:
                    send_txt(replies.content, group_chat)  # 假设send_txt方法接收内容和接收者ID
                elif replies.type == ReplyType.IMAGE:
                    send_img(replies.content, group_chat)  # 假设send_img方法接收图片URL和接收者ID

    def get_daily_news(self) -> Reply:
        reply_mode = self.config.get("reply_mode", "both")
        text_reply = Reply(ReplyType.TEXT, "获取早报失败，请稍后再试")
        image_reply = None
        try:
            token = self.config.get("token")  # 从配置中动态获取token
            payload = f"token={token}&format=json"
            headers = {'Content-Type': "application/x-www-form-urlencoded"}

            response = requests.request("POST", self.zaobao_api_url, data=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()['data']
                news_list = data['news']
                weiyu = data['weiyu']
                image = data['image']
                date = data['date']

                formatted_news = f"【今日早报】{date}\n"

                if reply_mode == "text" or reply_mode == "both":
                    formatted_news += "\n".join(news_list) + f"\n\n{weiyu}\n"
                    text_reply = Reply(ReplyType.TEXT, formatted_news)

                if reply_mode == "image" or reply_mode == "both":
                    image_reply = Reply(ReplyType.IMAGE, image)

                if image_reply:
                    return [text_reply, image_reply] if reply_mode == "both" else image_reply
                else:
                    return text_reply
            else:
                logger.error(f"Failed to fetch daily news: {response.text}")
        except Exception as e:
            logger.error(f"Error occurred while fetching daily news: {str(e)}")

    def did_receive_message(self, event: Event):
        pass

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "每日定时或手动发送早报"
