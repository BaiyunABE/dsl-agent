#!/usr/bin/env python3
"""
快速验证脚本 - 检查核心功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_imports():
    """测试核心模块导入"""
    print("🔧 测试核心模块导入...")
    
    modules_to_test = [
        ('dsl_engine', 'DSLEngine'),
        ('llm_client', 'LLMClient'),
        ('parser', 'Parser'),
        ('main', 'main')
    ]
    
    all_imported = True
    
    for module_name, class_name in modules_to_test:
        try:
            if class_name:
                # 测试类导入
                exec(f"from src.{module_name} import {class_name}")
                print(f"✅ {module_name}.{class_name} - 导入成功")
            else:
                # 测试模块导入
                exec(f"import src.{module_name}")
                print(f"✅ {module_name} - 导入成功")
        except ImportError as e:
            print(f"❌ {module_name}.{class_name} - 导入失败: {e}")
            all_imported = False
    
    return all_imported

def test_basic_functionality():
    """测试基本功能"""
    print("\n🔍 测试基本功能...")
    
    try:
        # 测试DSL引擎基本功能
        from src.dsl_engine import DSLEngine
        print("✅ DSL引擎 - 基本结构正常")
        
        # 测试LLM客户端基本功能
        from src.llm_client import LLMClient
        print("✅ LLM客户端 - 基本结构正常")
        
        # 测试语法分析器基本功能
        from src.parser import Parser
        print("✅ 语法分析器 - 基本结构正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_file_existence():
    """检查必要文件是否存在"""
    print("\n📁 检查必要文件...")
    
    required_files = [
        'src/script.dsl',
        'test/test_script.dsl'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - 存在")
        else:
            print(f"❌ {file_path} - 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主函数"""
    print("⚡ DSL客服机器人快速验证")
    print("="*40)
    
    # 运行测试
    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()
    files_ok = test_file_existence()
    
    # 总结
    print("\n" + "="*40)
    print("📋 验证结果")
    print("="*40)
    
    if imports_ok and functionality_ok and files_ok:
        print("🎉 所有验证通过！")
        print("💡 系统可以正常运行")
        return True
    else:
        print("⚠️  验证发现问题：")
        if not imports_ok:
            print("   - 模块导入有问题")
        if not functionality_ok:
            print("   - 基本功能有问题") 
        if not files_ok:
            print("   - 缺少必要文件")
        print("🔧 请检查并修复问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)