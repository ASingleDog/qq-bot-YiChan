# qq bot 伊酱
## 简介
娱乐向水群bot。
设计初心是希望能够融入群聊带来乐子，而不是要求使用者严格按照规定格式输入指令。
因此在关键词判定时，使用较为复杂的正则表达式判断，从而增强判断智能性、灵活性。
因考虑到轻量性，未使用数据库系统，适合于规模较小的应用。

## Ver.0.1.0 现有功能
使用kamiya.dev、aa1.cn等平台提供的api得以实现以下功能：
1. 群聊AI绘画（按格式自定义tag / 自然语言解析提取）
2. B站专栏沙雕图 / 小黑子 图爬虫爬取
3. B站专栏搜图
4. 水群聊天
5. 群聊复读机
6. 每日早安文章推荐

## 快速开始
1. 下载go-cqhttp并启动，上报端口可设置为5701
<a href='https://github.com/Mrs4s/go-cqhttp'>去go-cqhttp仓库</a>

2. 下载项目并完成 config.py 配置
3. 安装依赖
``
pip3 install -r requirements.txt
``
4. 执行程序
``
uvicorn main:app --reload --port 5701
``
