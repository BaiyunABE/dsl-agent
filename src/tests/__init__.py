"""
测试包初始化文件
"""

# 测试数据目录
TEST_DATA_DIR = 'tests/test_data'

def get_test_data_path(filename):
    """获取测试数据文件路径"""
    import os
    return os.path.join(os.path.dirname(__file__), 'test_data', filename)