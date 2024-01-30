import requests
import re
from plugins import register, Plugin, Event, Reply, ReplyType

@register
class GetJellyfin(Plugin):
    name = "get_jellyfin"

    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        self.user_id = config.get("user_id")
        self.movie_parent_ids = config.get("movie_parent_ids", [])
        self.series_parent_ids = config.get("series_parent_ids", [])
        self.web_url = config.get("web_url", "")

    def did_receive_message(self, event: Event):
        query = event.message.content.strip()
        is_group = event.message.is_group

        if is_group:
            query = re.sub(r'@[\w]+\s+', '', query, count=1).strip()

        commands = self.config.get("command", [])
        if any(re.search(r'\b' + re.escape(cmd) + r'\b', query) for cmd in commands):
            if query in ["最新电影", "有什么新电影", "最近有什么新电影"]:
                self.handle_movie_recommendation(event)
            elif query.startswith("搜索电影：") or query.startswith("查找电影："):
                movie_name = query.split("：", 1)[1]
                self.handle_movie_search(movie_name, event)
            elif query in ["最新电视剧", "有什么新剧", "最近有什么新剧"]:
                self.handle_series_recommendation(event)
            elif query.startswith("搜索电视剧：") or query.startswith("查找电视剧："):
                series_name = query.split("：", 1)[1]
                self.handle_series_search(series_name, event)
            event.bypass()

    def handle_movie_recommendation(self, event: Event):
        collection_names = ["合集1", "合集2", "合集3"]
        result_text = ""
        successful_request = False

        for parent_id, name in zip(self.movie_parent_ids, collection_names):
            base_url = self.base_url.rstrip('/')
            url = f"{base_url}/Users/{self.user_id}/Items?parentId={parent_id}&SortBy=DateCreated&SortOrder=Descending&IncludeItemTypes=Movie&fields=Name,CommunityRating&Limit=10&api_key={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                successful_request = True
                try:
                    movies = response.json()
                    result_text += f"最新{name}影片:\n"
                    for i, movie in enumerate(movies['Items'], 1):
                        movie_name = movie['Name']
                        rating = movie.get('CommunityRating')
                        rating_text = f"IMDB评分{rating}" if rating else "暂无评分"
                        result_text += f"{i}.《{movie_name}》{rating_text}\n"
                    result_text += "\n"
                except Exception as e:
                    result_text += f"处理{name}数据时发生错误: {e}\n\n"
            else:
                result_text += f"请求{name}数据失败，状态码：{response.status_code}\n\n"
        
        if not result_text:
            result_text = "无法获取最新电影信息，请稍后再试。"

        if successful_request and result_text.strip():
            result_text += f"观看地址(建议浏览器打开)：\n{self.web_url}"

        reply = Reply(ReplyType.TEXT, result_text.strip())
        event.channel.send(reply, event.message)

    def handle_movie_search(self, movie_name, event: Event):
        found = False
        result_text = ""

        for parent_id in self.movie_parent_ids:
            if not found:
                base_url = self.base_url.rstrip('/')
                url = f"{base_url}/Users/{self.user_id}/Items?parentId={parent_id}&SearchTerm={movie_name}&IncludeItemTypes=Movie&fields=Name,Overview,CommunityRating,PremiereDate&api_key={self.api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    try:
                        movies = response.json()
                        for item in movies['Items']:
                            if item['Name'] == movie_name:
                                result_text += "已找到符合的电影：\n"
                                result_text += f"电影名称：{item['Name']}\n"
                                rating = item.get('CommunityRating')
                                rating_text = f"IMDB评分：{rating}" if rating else "暂无评分"
                                result_text += f"{rating_text}\n"
                                premiere_date = item.get('PremiereDate', '未知').split('T')[0]
                                result_text += f"上映时间：{premiere_date}\n"
                                result_text += f"剧情简介：\n{item.get('Overview', '无简介')}\n\n"
                                found = True
                                break
                    except Exception as e:
                        result_text += f"JSON解析错误: {e}\n"
                else:
                    result_text += f"请求失败，状态码：{response.status_code}\n"
        
        if not found:
            result_text = "未找到符合的电影，请检查名称或联系管理员上传。" if not result_text else result_text

        if found:
            result_text += f"观看地址(建议浏览器打开)：\n{self.web_url}"

        reply = Reply(ReplyType.TEXT, result_text.strip())
        event.channel.send(reply, event.message)

    def handle_series_recommendation(self, event: Event):
        collection_names = ["电视剧"]
        result_text = ""
        successful_request = False

        for parent_id, name in zip(self.series_parent_ids, collection_names):
            base_url = self.base_url.rstrip('/')
            url = f"{base_url}/Users/{self.user_id}/Items?parentId={parent_id}&SortBy=DateCreated&SortOrder=Descending&IncludeItemTypes=Series&fields=Name,CommunityRating,PremiereDate&Limit=5&api_key={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                successful_request = True
                try:
                    series = response.json()
                    result_text += f"最新{name}剧集:\n"
                    for i, item in enumerate(series['Items'], 1):
                        series_name = item['Name']
                        rating = item.get('CommunityRating')
                        rating_text = f"IMDB评分{rating}" if rating else "暂无评分"
                        result_text += f"{i}.《{series_name}》{rating_text}\n"
                    result_text += "\n"
                except Exception as e:
                    result_text += f"处理{name}数据时发生错误: {e}\n\n"
            else:
                result_text += f"请求{name}数据失败，状态码：{response.status_code}\n\n"

        if successful_request and result_text.strip():
            result_text += f"观看地址(建议浏览器打开)：\n{self.web_url}"

        reply = Reply(ReplyType.TEXT, result_text.strip())
        event.channel.send(reply, event.message)
    
    def handle_series_search(self, series_name, event: Event):
        found = False
        result_text = ""

        for parent_id in self.series_parent_ids:
            if not found:
                base_url = self.base_url.rstrip('/')
                url = f"{base_url}/Users/{self.user_id}/Items?parentId={parent_id}&SearchTerm={series_name}&IncludeItemTypes=Series&fields=Name,Overview,CommunityRating&api_key={self.api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    try:
                        series = response.json()      
                        for item in series['Items']:
                            if item['Name'] == series_name:
                                result_text += "已找到符合的剧集：\n"
                                result_text += f"剧集名称：{item['Name']}\n"
                                rating = item.get('CommunityRating')
                                rating_text = f"IMDB评分：{rating}" if rating else "暂无评分"
                                result_text += f"{rating_text}\n"
                                premiere_date = item.get('PremiereDate', '未知').split('T')[0]
                                result_text += f"首播时间：{premiere_date}\n"
                                result_text += f"剧情简介：\n{item.get('Overview', '无简介')}\n\n"
                                found = True
                                break
                    except Exception as e:
                        result_text += f"JSON解析错误: {e}\n"
                else:
                    result_text += f"请求失败，状态码：{response.status_code}\n"
        
        if not found:
            result_text = "未找到符合的剧集，请检查名称或联系管理员上传。" if not result_text else result_text

        if found:
            result_text += f"观看地址(建议浏览器打开)：\n{self.web_url}"

        reply = Reply(ReplyType.TEXT, result_text.strip())
        event.channel.send(reply, event.message)

    def help(self, **kwargs) -> str:
        return "发送特定关键词以获取最新电影或搜索特定电影。例如：'电影推荐', '最新电影', '搜索电影：[电影名]'。"

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def will_generate_reply(self, event: Event):
        pass
