import requests
from plugins import register, Plugin, Event, logger, Reply, ReplyType

@register
class DailyNews(Plugin):
    name = "daily_news"
    zaobao_api_url = "https://v2.alapi.cn/api/zaobao"

    def __init__(self, config):
        super().__init__(config)
    
    def did_receive_message(self, event: Event):
        pass

    def will_generate_reply(self, event: Event):
        query = event.message.content.strip()
        commands = self.config.get("command", [])
        if any(cmd in query for cmd in commands):
            replies = self.get_daily_news()
            if isinstance(replies, list):
                for reply in replies:
                    event.channel.send(reply, event.message)
            else:
                event.reply = replies
            event.bypass()

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
    
    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "使用命令 #早报 (或者您在配置中设置的任何命令) 来获取每日早报"

        return text_reply
