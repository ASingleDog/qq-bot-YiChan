# qq bot 伊酱
## 简介
娱乐向水群bot。
设计初心是希望能够自然点融入群聊带来乐子，因此在关键词判定时，使用较为复杂的正则表达式判断，希望能更灵活智能。
因考虑到轻量性，目前未使用数据库系统，适合于规模较小的应用。

## Ver.0.2.0 重要更新
接入ChatGPT, 优化聊天体验（连续应答参数改动，水群聊天加入表情包）

## Ver.0.2 现有功能
1. 群聊AI绘画（按格式自定义tag / 自然语言解析提取）
2. B站专栏沙雕图 / 小黑子 图爬虫爬取
3. B站专栏搜图
4. 水群聊天，目前支持随机发送水群表情
5. 群聊复读机
6. 接入ChatGPT (条件受限无法保留上下文)

使用了kamiya.dev、aa1.cn等平台提供的api，在此表示感谢。

## 快速开始
1. 下载go-cqhttp并启动，上报地址请设置为`http://127.0.0.1:5701`
<a href='https://github.com/Mrs4s/go-cqhttp'>点这里去go-cqhttp仓库</a>

2. 下载项目并完成 config.py 配置
3. 安装依赖
``
pip3 install -r requirements.txt
``
4. 执行程序
``
uvicorn main:app --reload --port 5701
``
