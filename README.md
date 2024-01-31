# wechat-gptbot 获取Jellyfin媒体库信息插件

本项目作为 `wechat-gptbot` 插件，可以根据关键字回复对应的信息。

## 安装指南

### 1. 添加插件源
在 `plugins/source.json` 文件中添加以下配置：
```
{
  "news_hub": {
    "repo": "https://github.com/lepingzhang/get_jellyfin.git",
    "desc": "发送特定关键词以获取最新电影或搜索特定电影"
  }
}
```

### 2. 插件配置
在 `config.json` 文件中添加以下配置：
```
"plugins": [
  {
    "name": "get_jellyfin",
    "command": ["最新电影", "有什么新电影", "最近有什么新电影", "搜索电影：", "查找电影：", "最新电视剧", "有什么新剧", "最近有什么新剧", "搜索电视剧：", "查找电视剧："],
    "base_url": "your_jellyfin_server",
    "web_url": "your_jellyfin_web",
    "api_key": "your_jellyfin_api",
    "user_id": "your_jellyfin_user_id",
    "movie_parent_ids": ["parent_id1", "parent_id2", "parent_id3"],
    "series_parent_ids": ["parent_id1"]
  }
]
```

### 3. 修改合集名称
在代码的`collection_names`部分，修改为你的合集名称，即对应的`parent_id`的名称。
