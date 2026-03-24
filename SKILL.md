---
name: ai-news-scraper
description: 爬取36氪AI资讯并生成摘要版TXT文档；当用户需要获取AI行业资讯、生成每日资讯汇总或收集AI相关文章时使用
dependency:
  python:
    - requests>=2.31.0
    - beautifulsoup4>=4.12.0
    - lxml>=5.0.0
  system:
    - python scripts/check_env.sh
    - pip install -q requests beautifulsoup4 lxml
---

# 36氪AI资讯爬虫

## 任务目标
- 本 Skill 用于：爬取36氪AI资讯页面最新的20条资讯，提取原文并生成摘要版TXT文档
- 信源地址：https://www.36kr.com/information/AI/
- 爬取数量：**固定爬取最新的20条资讯**
- 能力包含：网页内容抓取、HTML解析、原文提取、智能摘要生成、TXT文档输出
- 触发条件：用户需要获取AI行业资讯、生成每日资讯汇总或收集AI相关文章时

## 前置准备
- 依赖说明：爬虫脚本所需的Python包
  ```
  requests>=2.31.0
  beautifulsoup4>=4.12.0
  lxml>=5.0.0
  ```
- 环境准备：
  - Skill 会自动检测Python环境（需要 Python 3.6+）
  - 如果缺少Python，会提示安装命令
  - 如果缺少依赖包，会自动执行：`pip install -q requests beautifulsoup4 lxml`
  - 无需手动安装，直接调用脚本即可
  - 如需手动检查环境，可运行：`bash scripts/check_env.sh`
  - 如需手动检查依赖，可运行：`python scripts/install_deps.py`

## 操作步骤
- 标准流程：
  1. **环境检查与自动配置**
     - 智能体会自动检查Python环境（Python 3.6+）
     - 如果缺少Python，会提供安装命令提示
     - 如果缺少依赖包，会自动执行：`pip install -q requests beautifulsoup4 lxml`
  2. **执行爬虫脚本**
     - 调用 `scripts/web_scraper.py` 自动爬取36氪AI资讯
     - 脚本会自动访问信源地址：https://www.36kr.com/information/AI/
     - **固定爬取最新的20条资讯**（不可更改）
     - 对于每条资讯，会访问详情页获取完整的原文内容
  3. **生成临时原文文档**
     - 脚本将资讯列表转换为纯文本格式（包含原文）
     - 此文档仅供智能体阅读以生成摘要，不作为最终输出
  4. **智能体生成摘要**
     - 智能体阅读每条资讯的原文内容
     - 为每条资讯生成简洁摘要，**字数严格控制在100字以内**
     - 摘要生成要求：
       - 准确概括资讯的核心观点和关键信息
       - 提炼最重要的数据、结论或事件
       - 语言简洁，避免冗余表述
       - 不包含主观评价，仅陈述事实
       - 不使用"本文介绍了"、"文章讲述了"等套话开头
  5. **生成最终TXT文档**
     - 智能体将生成的摘要写入最终TXT文件
     - 文件名格式：`每日AI资讯_yyyymmdd.txt`（yyyymmdd为当天日期）
     - 文件编码：UTF-8
     - 最终格式：标题、【摘要】摘要内容、来源

## 资源索引
- 必要脚本：见 [scripts/web_scraper.py](scripts/web_scraper.py)（用途：爬取36氪AI资讯并生成TXT文档；自动检测Python环境和依赖；输出包含原文的完整资讯列表；参数：`--output` 指定TXT输出路径，默认 `ai_news-yyyymmdd.txt`）
- 环境检查脚本：见 [scripts/check_env.sh](scripts/check_env.sh)（用途：检查Python环境并提供安装建议；无需参数）
- 依赖检查脚本：见 [scripts/install_deps.py](scripts/install_deps.py)（用途：手动检查并安装依赖包；无需参数）

## 注意事项
- **爬取数量固定为最新的20条资讯，不可更改**
- 爬虫脚本已内置反爬虫处理（User-Agent伪装、请求延迟）
- 脚本会自动访问每篇文章的详情页以获取完整的原文内容
- 生成的TXT文档采用纯文本格式，便于知识切片和内容检索
- 请遵守36氪的使用条款和robots.txt协议
- 遇到403/404等HTTP错误时，可能是网站访问限制，请稍后重试
- 脚本会自动检测Python环境（需要Python 3.6+）和依赖包
- 如果Python环境缺失，脚本会提供各操作系统的安装命令

## 使用示例

### 示例1：爬取36氪AI资讯并生成TXT
```bash
python /workspace/projects/ai-news-scraper/scripts/web_scraper.py
# 默认输出为 ai_news-yyyymmdd.txt（yyyymmdd为当天日期）
```

### 示例2：指定TXT输出路径
```bash
python /workspace/projects/ai-news-scraper/scripts/web_scraper.py --output ./reports/ai_news.txt
```

## 输出格式说明

**脚本临时输出**（供智能体生成摘要使用，不作为最终输出）：
- 每条资讯包含：标题、【原文】原文内容、来源

**最终输出格式**（智能体生成的最终TXT文件）：
- 文件名：`每日AI资讯_yyyymmdd.txt`
- 每条资讯包含：
  - 标题（带序号）
  - 【摘要】摘要内容（不超过100字）
  - 来源

**摘要生成要求**：
- 智能体必须根据每条资讯的原文内容生成摘要
- 摘要字数严格控制在100字以内（中文按字符计数）
- 摘要应准确概括资讯核心观点和关键信息
- 提炼最重要的数据、结论或事件
- 语言简洁，避免冗余表述
- 不包含主观评价，仅陈述事实
- 不使用"本文介绍了"、"文章讲述了"等套话开头

**摘要示例**：
```
原文：OpenAI联合创始人Karpathy分享AI编程经验，称现在80%代码由Agent完成...

【摘要】OpenAI联合创始人Karpathy分享AI编程经验，称现在80%代码由Agent完成。他打造了名为"多比"的OpenClaw管理智能家居，并指出Agent做不好多半是Skill问题。
来源：智东西
```

**最终输出文件示例**（每日AI资讯_20260324.txt）：
```
1. AI大神卡帕西自曝：玩龙虾玩出"AI精神病"，token不烧完就焦虑
【摘要】OpenAI联合创始人Karpathy分享AI编程经验，称现在80%代码由Agent完成。他打造了名为"多比"的OpenClaw管理智能家居，并指出Agent做不好多半是Skill问题。
来源：智东西

2. 宇树净赚6亿：撕开遮羞布
【摘要】宇树机器人估值420亿，净赚6亿，产品均价从59万降到16.8万，毛利率达63%。其成功源于2016年早期入局、自研核心部件、靠产品而非PPT赚钱。
来源：铅笔道

3. 今年最豪华产业轮诞生
【摘要】物理AI公司江行智能完成数亿元B++轮融资，宁德系、晶科能源等产业资本集体押注。清华系团队创立八年，2025年订单达5亿并实现盈利。
来源：投资界
```

**输出文件要求**：
- 文件格式：TXT纯文本
- 文件编码：UTF-8
- 每条资讯之间空一行分隔
- 标题、摘要、来源各占一行
