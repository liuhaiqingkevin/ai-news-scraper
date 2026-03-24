#!/usr/bin/env bash
# 环境检测与自动安装脚本
# 功能：检测Python环境，如果不存在则尝试安装

echo "检查Python环境..." >&2

# 检查Python是否已安装
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✓ 找到 Python3: $(python3 --version)" >&2
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✓ 找到 Python: $(python --version)" >&2
else
    echo "✗ 未找到Python环境" >&2
    echo "" >&2
    echo "尝试自动安装Python..." >&2
    
    # 检测操作系统并尝试安装
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        echo "检测到 Ubuntu/Debian 系统" >&2
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        echo "检测到 CentOS/RHEL 系统" >&2
        sudo yum install -y python3 python3-pip
    elif command -v brew &> /dev/null; then
        # macOS (Homebrew)
        echo "检测到 macOS 系统" >&2
        brew install python3
    else
        echo "无法自动安装Python，请手动安装后重试" >&2
        echo "" >&2
        echo "安装建议：" >&2
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip" >&2
        echo "  CentOS/RHEL: sudo yum install python3 python3-pip" >&2
        echo "  macOS: brew install python3" >&2
        echo "  Windows: 从 https://www.python.org/downloads/ 下载安装" >&2
        exit 1
    fi
    
    # 重新检查
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Python安装失败，请手动安装" >&2
        exit 1
    fi
fi

# 检查pip是否可用
echo "" >&2
echo "检查pip..." >&2
if $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "✓ pip 已安装" >&2
else
    echo "✗ pip 未安装，尝试安装..." >&2
    $PYTHON_CMD -m ensurepip --upgrade
fi

# 输出Python命令路径
echo $PYTHON_CMD
