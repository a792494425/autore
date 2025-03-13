#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据清理脚本
功能：去除文本中的所有空格、制表符、换行符等空白字符
"""

import os
import re

def clean_text(text):
    """
    去除文本中的所有空白字符（空格、制表符、换行符等）
    
    参数:
        text (str): 原始文本
    
    返回:
        str: 清理后的纯文本（不包含任何空白字符）
    """
    return ''.join(text.split())

def clean_from_input():
    """从用户输入获取文本并清理"""
    print("请输入或粘贴要处理的文本（输入完成后按两次回车结束）：")
    
    lines = []
    while True:
        line = input()
        if not line:  # 如果是空行，结束输入
            break
        lines.append(line)
    
    # 合并所有输入行
    input_text = "\n".join(lines)
    
    # 显示原始文本信息
    print(f"\n原始文本长度: {len(input_text)} 字符")
    print(f"原始文本行数: {len(lines)} 行")
    
    # 清理文本
    cleaned_text = clean_text(input_text)
    
    # 显示清理后的文本信息
    print(f"\n清理后的文本长度: {len(cleaned_text)} 字符")
    print("所有空格、换行和空白字符已移除")
    
    # 询问用户是否要查看清理后的文本
    show_text = input("\n是否显示清理后的文本？(y/n): ")
    if show_text.lower() == 'y':
        print("\n清理后的文本:")
        print("="*50)
        print(cleaned_text)
        print("="*50)
    
    # 询问用户是否要保存到文件
    save_to_file = input("\n是否保存到文件？(y/n): ")
    if save_to_file.lower() == 'y':
        filename = input("请输入文件名（默认为 cleaned_data.txt）: ") or "cleaned_data.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        print(f"文件已保存为: {os.path.abspath(filename)}")
    
    return cleaned_text

def clean_from_file(input_file, output_file=None):
    """从文件读取文本并清理"""
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
        
        # 显示原始文本信息
        print(f"\n原始文件: {input_file}")
        print(f"原始文本长度: {len(input_text)} 字符")
        
        # 清理文本
        cleaned_text = clean_text(input_text)
        
        # 显示清理后的文本信息
        print(f"\n清理后的文本长度: {len(cleaned_text)} 字符")
        print("所有空格、换行和空白字符已移除")
        
        # 如果指定了输出文件，保存清理后的文本
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            print(f"清理后的文本已保存到: {output_file}")
        
        return cleaned_text
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return None

def main():
    """主函数"""
    print("文本数据清理工具 - 去除所有空格和换行")
    print("=" * 40)
    
    while True:
        print("\n请选择操作:")
        print("1. 输入或粘贴文本进行处理")
        print("2. 从文件读取文本进行处理")
        print("3. 退出")
        
        choice = input("请选择 [1/2/3]: ")
        
        if choice == '1':
            clean_from_input()
        elif choice == '2':
            input_file = input("请输入源文件路径: ")
            save_option = input("是否保存处理后的文本到文件? (y/n): ")
            
            if save_option.lower() == 'y':
                output_file = input("请输入目标文件路径（默认为 cleaned_data.txt）: ") or "cleaned_data.txt"
                clean_from_file(input_file, output_file)
            else:
                clean_from_file(input_file)
        elif choice == '3':
            print("感谢使用，再见!")
            break
        else:
            print("无效的选择，请重试。")

if __name__ == "__main__":
    main() 