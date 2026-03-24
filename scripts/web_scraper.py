#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
36氪AI资讯爬虫
功能：爬取36氪AI资讯，提取完整内容，生成TXT文档
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
import subprocess
import re

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("正在自动安装依赖包...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "requests", "beautifulsoup4"])
    import requests
    from bs4 import BeautifulSoup


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"错误: 需要Python 3.6或更高版本，当前版本: {sys.version}")
        print("\n安装Python:")
        print("  Ubuntu/Debian: sudo apt-get install python3")
        print("  CentOS/RHEL: sudo yum install python3")
        print("  macOS: brew install python3")
        print("  Windows: 访问 https://www.python.org/downloads/ 下载安装")
        sys.exit(1)
    print(f"✓ Python环境: {sys.version.split()[0]}")


def check_dependencies():
    """检查并安装依赖包"""
    required_packages = {
        'requests': '>=2.31.0',
        'beautifulsoup4': '>=4.12.0',
        'lxml': '>=5.0.0'
    }
    
    missing_packages = []
    
    for package, version_spec in required_packages.items():
        try:
            module_name = package.replace('-', '_')
            if package == 'beautifulsoup4':
                module_name = 'bs4'
            
            __import__(module_name)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n正在安装缺失的依赖包: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-q",
                *missing_packages
            ])
            print("✓ 所有依赖包安装完毕")
        except subprocess.CalledProcessError as e:
            print(f"✗ 依赖包安装失败: {e}")
            sys.exit(1)


def fetch_page(url, max_retries=3):
    """获取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败 (状态码: {response.status_code}), 重试 {attempt + 1}/{max_retries}...")
                time.sleep(2)
        except Exception as e:
            print(f"请求异常: {e}, 重试 {attempt + 1}/{max_retries}...")
            time.sleep(2)
    
    return None


def filter_unwanted_content(text):
    """过滤不需要的内容"""
    if not text:
        return ''
    
    # 图片相关关键词
    image_keywords = [
        r'图源[:：]\s*[^\n]*',
        r'图片来源[:：]\s*[^\n]*',
        r'图片说明[:：]\s*[^\n]*',
        r'图片来自[:：]\s*[^\n]*',
        r'图片来源\s*[^\n]*',
        r'图\s*[:：]\s*[^\n]*',
        r'配图[:：]\s*[^\n]*',
        r'图片\s*[^\n]*',
    ]
    
    # 参考资料和声明相关关键词
    reference_keywords = [
        r'参考资料[:：]\s*[^\n]*',
        r'参考来源[:：]\s*[^\n]*',
        r'参考资料\s*[^\n]*',
        r'参考文献[:：]\s*[^\n]*',
        r'来源\s*[：:]\s*[^\n]*',
        r'本文\s*来源\s*[：:]\s*[^\n]*',
        r'授权发布[:：]\s*[^\n]*',
        r'未经授权\s*禁止转载\s*[^\n]*',
        r'观点\s*代表\s*本人\s*[^\n]*',
        r'观点\s*仅\s*代表\s*个人\s*[^\n]*',
        r'文中\s*观点\s*不\s*代表\s*[^\n]*',
        r'本文\s*观点\s*仅\s*代表\s*[^\n]*',
        r'声明[:：]\s*[^\n]*',
        r'免责声明[:：]\s*[^\n]*',
        r'免责\s*声明\s*[^\n]*',
        r'转载\s*请\s*注明\s*[^\n]*',
        r'本文\s*系\s*授权\s*[^\n]*',
        r'本文\s*为\s*授权\s*[^\n]*',
        # 作者和编辑信息（通常出现在文章开头）
        r'作者[:｜]\s*[^\n]*',
        r'编辑[:｜]\s*[^\n]*',
    ]
    
    # 合并所有过滤规则
    all_keywords = image_keywords + reference_keywords
    
    # 逐行过滤
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检查是否包含过滤关键词
        should_filter = False
        for pattern in all_keywords:
            if re.search(pattern, line, re.IGNORECASE):
                should_filter = True
                break
        
        if not should_filter:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def parse_article_list(html):
    """解析资讯列表"""
    soup = BeautifulSoup(html, 'lxml')
    articles = []
    
    # 36氪资讯列表的CSS选择器
    article_items = soup.select('div.information-flow-item')
    
    print(f"尝试解析资讯列表，找到 {len(article_items)} 个元素")
    
    if not article_items:
        # 尝试其他可能的选择器
        article_items = soup.select('article.item')
        print(f"尝试备选选择器，找到 {len(article_items)} 个元素")
    
    if not article_items:
        print("警告: 未找到资讯列表，可能网站结构已变化")
    
    for item in article_items:
        try:
            # 提取标题和链接 - 使用实际存在的选择器
            title_elem = item.select_one('a.article-item-title')
            
            if not title_elem:
                # 尝试其他可能的选择器
                title_elem = item.select_one('p.title-wrapper a')
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                # 处理相对URL
                if url and not url.startswith('http'):
                    url = f"https://www.36kr.com{url}"
                
                # 提取来源（从列表页的 kr-flow-bar-author 获取）
                source_elem = item.select_one('a.kr-flow-bar-author')
                source = source_elem.get_text(strip=True) if source_elem else '36氪'
                
                # 提取摘要 - 使用实际的选择器
                summary_elem = item.select_one('a.article-item-description')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'source': source
                    })
                    print(f"  解析到文章: {title[:50]}... (来源: {source})")
        except Exception as e:
            print(f"解析文章项时出错: {e}")
            continue
    
    print(f"成功解析 {len(articles)} 篇文章")
    return articles


def fetch_article_content(article_url, source_from_list=None):
    """获取文章详情页内容
    
    Args:
        article_url: 文章详情页URL
        source_from_list: 从列表页获取的来源（优先使用）
    """
    html = fetch_page(article_url)
    if not html:
        return None, None, []
    
    soup = BeautifulSoup(html, 'lxml')
    
    # 使用列表页传递的来源，如果没有则从详情页提取
    if source_from_list:
        source = source_from_list
    else:
        # 从详情页的文章标题中提取来源（如"硬氪首发"、"最前线"等）
        source = '36氪'  # 默认值
        
        # 从文章标题中提取来源（格式：标题 | 来源）
        title_elem = soup.select_one('h1.article-title')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # 匹配 "标题 | 来源" 格式
            match = re.search(r'\|\s*(.+?)$', title_text)
            if match:
                source = match.group(1).strip()
            else:
                # 尝试从title标签提取（格式：标题 | 来源-36氪）
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text(strip=True)
                    match = re.search(r'(.+?)\|(.+?)\s*-\s*36氪', title_text)
                    if match:
                        source = match.group(2).strip()
    
    # 提取发布时间（不在PDF中显示，但保留数据）
    time_elem = soup.select_one('span.article-item-time')
    if not time_elem:
        time_elem = soup.select_one('time.publish-time')
    publish_time = time_elem.get_text(strip=True) if time_elem else ''
    
    # 格式化发布时间为 yyyy-mm-dd
    if publish_time:
        try:
            # 尝试多种日期格式
            for fmt in ['%Y-%m-%d', '%Y年%m月%d日', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(publish_time[:10], fmt)
                    publish_time = dt.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
        except Exception:
            pass
    
    # 提取文章正文（保持原始分段）
    content_elem = soup.select_one('div.article-content')
    if not content_elem:
        content_elem = soup.select_one('div.markdown-body')
    
    content_elements = []
    
    # 需要跳过的类名
    skip_classes = ['image-wrapper', 'img-desc', 'article-footer-txt']
    
    # 需要过滤的内容模式
    filter_patterns = [
        r'^作者[:｜]\s*',          # 作者行
        r'^编辑[:｜]\s*',          # 编辑行
        r'^\d{4}年\d{2}月\d{2}日', # 日期行
        r'^本文由「',              # 版权声明
        r'转载说明',              # 转载说明
        r'寻求报道',              # 寻求报道
        r'企业授权',              # 图片授权
        r'本文图片来自',          # 图片来源
        r'违规转载必究',          # 转载声明
        r'^·\s*$',                # 单独的点号
    ]
    
    if content_elem:
        # 递归查找所有p标签
        for p in content_elem.find_all('p', recursive=True):
            # 检查是否包含需要跳过的类名
            elem_classes = p.get('class', [])
            if any(cls in elem_classes for cls in skip_classes):
                continue
            
            text = p.get_text(strip=True)
            if not text:
                continue
            
            # 检查是否匹配过滤模式
            should_filter = False
            for pattern in filter_patterns:
                if re.search(pattern, text):
                    should_filter = True
                    break
            
            if should_filter:
                continue
            
            # 使用原有的过滤函数进行二次过滤
            filtered_text = filter_unwanted_content(text)
            
            # 额外检查：过滤掉只包含标点符号的段落
            if filtered_text:
                # 检查是否只包含标点符号和空格
                import string
                # 去除所有标点符号和空格
                cleaned = filtered_text.strip(string.whitespace + string.punctuation + '「」『』【】（）()《》〈〉""''')
                if cleaned:  # 如果去除了标点后还有内容，才保留
                    content_elements.append({
                        'type': 'paragraph',
                        'text': filtered_text
                    })
    
    return source, content_elements


def generate_text(articles, date_str):
    """生成TXT内容（包含原文，供智能体生成摘要使用）"""
    text_parts = []
    
    # 每篇文章
    for i, article in enumerate(articles, 1):
        # 标题
        text_parts.append(f"{i}. {article['title']}")
        text_parts.append("")
        
        # 原文（供智能体生成摘要使用）
        text_parts.append("【原文】")
        for element in article.get('content_elements', []):
            if element['type'] == 'paragraph':
                text_parts.append(element['text'])
        text_parts.append("")
        
        # 来源
        text_parts.append(f"来源：{article['source']}")
        text_parts.append("")
    
    return '\n'.join(text_parts)


def generate_txt(text_content, output_path):
    """生成TXT文档"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"✓ TXT文档已生成: {output_path}")
        return True
    except Exception as e:
        print(f"✗ TXT文档生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 获取当前日期
    date_str = datetime.now().strftime('%Y-%m-%d')
    date_compact = datetime.now().strftime('%Y%m%d')
    
    # 设置默认输出文件名
    default_output = f'ai_news-{date_compact}.txt'
    
    parser = argparse.ArgumentParser(description='36氪AI资讯爬虫')
    parser.add_argument('--output', '-o', default=default_output, help=f'TXT输出路径 (默认: {default_output})')
    parser.add_argument('--json-output', '-j', help='JSON数据输出路径 (可选)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("36氪AI资讯爬虫")
    print("=" * 60)
    
    # 检查环境
    print("\n[1/4] 检查Python环境...")
    check_python_version()
    
    # 检查依赖
    print("\n[2/4] 检查依赖包...")
    check_dependencies()
    
    # 爬取列表页
    print("\n[3/4] 爬取资讯列表...")
    url = "https://www.36kr.com/information/AI/"
    print(f"目标URL: {url}")
    
    html = fetch_page(url)
    if not html:
        print("✗ 获取页面失败")
        sys.exit(1)
    
    articles = parse_article_list(html)
    print(f"✓ 找到 {len(articles)} 条资讯")
    
    # 只取最新的20条资讯
    MAX_ARTICLES = 20
    if len(articles) > MAX_ARTICLES:
        articles = articles[:MAX_ARTICLES]
        print(f"✓ 限制爬取数量为最新 {MAX_ARTICLES} 条")
    
    if not articles:
        print("未找到任何资讯，程序退出")
        sys.exit(0)
    
    # 爬取每篇文章的详情
    print(f"\n[4/4] 爬取文章详情...")
    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] 正在获取: {article['title'][:30]}...")
        
        # 传递列表页获取的来源，优先使用
        source_from_list = article.get('source', None)
        source, content_elements = fetch_article_content(article['url'], source_from_list)
        
        # 如果列表页有来源，使用列表页的；否则使用详情页提取的
        if source_from_list:
            article['source'] = source_from_list
        elif source:
            article['source'] = source
        
        # 保存内容元素（保持原始分段）
        article['content_elements'] = content_elements
        
        # 如果没有内容元素，使用摘要作为content
        if not content_elements:
            article['content_elements'] = [{'type': 'paragraph', 'text': article['summary']}]
        
        # 添加延迟，避免被封
        time.sleep(1)
    
    print(f"✓ 完成所有文章详情获取")
    
    # 生成TXT
    print(f"\n生成TXT文档...")
    text_content = generate_text(articles, date_str)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成TXT
    if generate_txt(text_content, args.output):
        print(f"\n✓ 任务完成！TXT文档已保存到: {args.output}")
        
        # 如果需要，也输出JSON
        if args.json_output:
            with open(args.json_output, 'w', encoding='utf-8') as f:
                json.dump({
                    'success': True,
                    'total': len(articles),
                    'data': articles,
                    'message': '爬取成功'
                }, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON数据已保存到: {args.json_output}")
    else:
        print("\n✗ TXT文档生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
