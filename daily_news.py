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
        if query == self.config.get("command"):
            event.reply = self.get_daily_news()
            event.bypass()
    
    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "使用命令 #早报 (或者您在配置中设置的任何命令) 来获取每日早报"

    def get_daily_news(self) -> Reply:
        reply_mode = self.config.get("reply_mode", "both")
        reply = Reply(ReplyType.TEXT, "获取早报失败，请稍后再试")
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
                head_image = data['head_image']
                date = data['date']

                formatted_news = f"【今日早报】{date}\n"

                if reply_mode == "text" or reply_mode == "both":
                    formatted_news += "\n".join(news_list) + f"\n\n微语：{weiyu}\n\n早报头图：{head_image}\n"

                if reply_mode == "image" or reply_mode == "both":
                    formatted_news += f"早报图片：{image}"

                reply = Reply(ReplyType.TEXT, formatted_news)
            else:
                logger.error(f"Failed to fetch daily news: {response.text}")
        except Exception as e:
            logger.error(f"Error occurred while fetching daily news: {str(e)}")

        return reply
