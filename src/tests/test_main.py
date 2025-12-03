"""
主程序测试用例
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
import argparse
from main import parse_arguments

class TestMain:
    def test_parse_arguments(self):
        """测试命令行参数解析"""
        # 测试正常情况
        test_args = ['test_script.dsl', '--debug']
        with patch('sys.argv', ['main.py'] + test_args):
            args = parse_arguments()
            assert args.script == 'test_script.dsl'
            assert args.debug == True
        
        # 测试无调试模式
        test_args = ['test_script.dsl']
        with patch('sys.argv', ['main.py'] + test_args):
            args = parse_arguments()
            assert args.script == 'test_script.dsl'
            assert args.debug == False