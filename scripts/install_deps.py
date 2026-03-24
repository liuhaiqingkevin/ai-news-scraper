#!/usr/bin/env python3
"""
依赖检查与安装脚本
功能：检查并安装Skill所需的Python依赖包
"""

import subprocess
import sys


def check_and_install_dependencies():
    """
    检查并安装依赖包
    
    Returns:
        bool: 是否成功
    """
    required_packages = {
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'lxml': 'lxml',
        'weasyprint': 'weasyprint'
    }
    
    missing_packages = []
    
    # 检查缺失的包
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} 已安装", file=sys.stderr)
        except ImportError:
            print(f"✗ {package_name} 未安装", file=sys.stderr)
            missing_packages.append(package_name)
    
    if not missing_packages:
        print("\n所有依赖包已安装完毕，可以直接运行爬虫脚本。", file=sys.stderr)
        return True
    
    # 安装缺失的包
    print(f"\n开始安装缺失的依赖包: {', '.join(missing_packages)}", file=sys.stderr)
    
    try:
        install_command = ['pip', 'install', '-q'] + missing_packages
        subprocess.check_call(install_command)
        
        print("依赖包安装成功！", file=sys.stderr)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}", file=sys.stderr)
        print("\n请手动运行以下命令安装依赖：", file=sys.stderr)
        print(f"pip install {' '.join(missing_packages)}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"安装过程中发生错误: {e}", file=sys.stderr)
        return False


if __name__ == '__main__':
    success = check_and_install_dependencies()
    sys.exit(0 if success else 1)
