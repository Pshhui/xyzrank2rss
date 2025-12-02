import json
import datetime
from xml.sax.saxutils import escape

# ================= 配置区域 =================
# ⚠️ 确认你的 json 文件路径是否正确，如果文件名不一样，请修改这里
INPUT_JSON_FILE = 'https://github.com/eddiehe99/xyzrank/raw/refs/heads/main/hot_episodes.json' # 假设这是你的热榜文件名
OUTPUT_RSS_FILE = 'hot_episodes_feed.xml'
# ===========================================

def create_rss_item(episode):
    # 1. 数据清洗和字段映射
    title = escape(episode.get('title', ''))
    link = escape(episode.get('link', '')) # 小宇宙的网页链接
    podcast_name = escape(episode.get('podcastName', ''))
    logo_url = escape(episode.get('logoURL', ''))
    
    # 2. 描述内容，将播客名和链接加入描述
    description = f"来自播客: {podcast_name}. 点击链接跳转到小宇宙页面：{link}"
    
    # 3. 日期格式转换 (将 ISO 时间转换为 RSS 标准时间)
    try:
        # 现代 Python 版本可以直接解析 ISO 格式
        post_time_str = episode.get('postTime', '')
        if post_time_str:
            # 替换 Z 为 +00:00 以兼容 fromisoformat
            dt_object = datetime.datetime.fromisoformat(post_time_str.replace('Z', '+00:00'))
            rss_pub_date = dt_object.strftime("%a, %d %b %Y %H:%M:%S GMT")
        else:
            rss_pub_date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    except Exception:
        rss_pub_date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    # 4. 生成 RSS Item 结构
    return f"""
    <item>
      <title>{title} | {podcast_name}</title>
      <link>{link}</link>
      <description>{description}</description>
      
      <enclosure url="{link}" type="text/html" />
      
      <guid isPermaLink="false">{link}</guid>
      <pubDate>{rss_pub_date}</pubDate>
      <itunes:image href="{logo_url}" />
    </item>
    """

def generate_rss():
    try:
        with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 核心修改：读取 episodes 列表
        episodes = data.get('data', {}).get('episodes', []) 

        if not episodes:
            print("❌ 警告：JSON 文件中未找到 episodes 列表，跳过 RSS 生成。")
            return

        rss_items = "".join([create_rss_item(ep) for ep in episodes])

        # 整个 RSS Feed 的元数据
        rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>XYZRank 每日热榜 (Podwise 专用)</title>
    <link>https://github.com/cellinlab/xyzrank</link>
    <description>由 GitHub Action 自动抓取并转换为 Podwise 专用的播客热榜。注意：内容为网页链接，非音频直链。</description>
    <language>zh-cn</language>
    <itunes:image href="https://img.logo.com/xyzrank_logo.png" />
    {rss_items}
  </channel>
</rss>
"""
        with open(OUTPUT_RSS_FILE, 'w', encoding='utf-8') as f:
            f.write(rss_content)
        print(f"✅ 成功生成 RSS 文件: {OUTPUT_RSS_FILE}")

    except FileNotFoundError:
        print(f"❌ 错误：未找到 JSON 文件 '{INPUT_JSON_FILE}'，请检查文件名和路径。")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

if __name__ == "__main__":
    generate_rss()
