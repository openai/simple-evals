#!/usr/bin/env python3

import sys
import os
import argparse

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入 simple_evals 模块
import simple_evals

if __name__ == "__main__":
    # 解析命令行参数
    sys.argv = sys.argv[:]  # 创建argv副本
    # 运行主函数
    simple_evals.main()