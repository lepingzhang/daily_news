# wechat-gptbot每日早报插件

本项目作为 `wechat-gptbot` 插件，可以根据关键字回复对应的信息。

## 安装指南

### 1. 添加插件源
在 `plugins/source.json` 文件中添加以下配置：
```
{
  "keyword_reply": {
    "repo": "https://github.com/lepingzhang/daily_news.git",
    "desc": "每日早报"
  }
}
```

### 2. 插件配置
在 `config.json` 文件中添加以下配置：
```
"plugins": [
  {
    "name": "daily_news",
    "schedule_time": "08:00",
    "command": ["早报", "新闻", "今天有什么新闻"],
    "single_chat_list": ["wxid_***"], 
    "group_chat_list": ["***@chatroom"],
    "token": "your_token_here",
    "reply_mode": "both" #text仅文本、image仅图片、both文本+图片
  }
]
```
