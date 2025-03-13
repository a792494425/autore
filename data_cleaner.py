#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据清理脚本
功能：去除文本中的所有空格、制表符、换行符等空白字符，并提取手机号
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

def extract_phone_numbers(text):
    """
    从文本中提取中国大陆手机号
    
    参数:
        text (str): 要提取手机号的文本
        
    返回:
        list: 提取到的手机号列表
    """
    phone_numbers = []
    i = 0
    while i <= len(text) - 11:  # 需要至少11个字符才能形成手机号
        # 检查当前位置开始的11个字符是否是手机号
        potential_phone = text[i:i+11]
        
        # 检查是否符合中国大陆手机号的格式（1开头的11位数字）
        if potential_phone[0] == '1' and potential_phone.isdigit():
            # 进一步验证第二位是否在3-9之间
            if '3' <= potential_phone[1] <= '9':
                phone_numbers.append(potential_phone)
                # 跳过这个手机号的剩余部分
                i += 11
                continue
        
        # 移动到下一个字符
        i += 1
    
    # 去除重复的手机号
    return list(set(phone_numbers))

def clean_from_input():
    """从用户输入获取文本并清理"""
    print("请输入或粘贴要处理的文本")
    print("输入完成后，请键入'END'然后按回车结束输入")
    print("这样可以确保处理所有数据，即使其中包含空行")
    
    lines = []
    print("\n请开始输入文本（输入'END'结束）：")
    while True:
        line = input()
        if line.strip() == "END":  # 使用特定标记结束输入
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
    
    # 提取手机号
    phone_numbers = extract_phone_numbers(cleaned_text)
    
    # 显示提取到的手机号
    if phone_numbers:
        print("\n从清理后的文本中提取到的手机号:")
        for i, phone in enumerate(phone_numbers):
            print(f"{i+1}. {phone}")
        print(f"共找到 {len(phone_numbers)} 个手机号")
    else:
        print("\n未找到任何手机号")
    
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
        
        # 询问是否保存提取到的手机号
        if phone_numbers:
            save_phones = input("是否保存提取到的手机号到文件? (y/n): ")
            if save_phones.lower() == 'y':
                phone_filename = input("请输入手机号文件名（默认为 phone_numbers.txt）: ") or "phone_numbers.txt"
                with open(phone_filename, 'w', encoding='utf-8') as f:
                    for phone in phone_numbers:
                        f.write(phone + '\n')
                print(f"手机号已保存为: {os.path.abspath(phone_filename)}")
    
    return cleaned_text, phone_numbers

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
        
        # 提取手机号
        phone_numbers = extract_phone_numbers(cleaned_text)
        
        # 显示提取到的手机号
        if phone_numbers:
            print("\n从清理后的文本中提取到的手机号:")
            for i, phone in enumerate(phone_numbers):
                print(f"{i+1}. {phone}")
            print(f"共找到 {len(phone_numbers)} 个手机号")
        else:
            print("\n未找到任何手机号")
        
        # 如果指定了输出文件，保存清理后的文本
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            print(f"清理后的文本已保存到: {output_file}")
            
            # 如果找到了手机号，询问是否保存
            if phone_numbers:
                save_phones = input("是否保存提取到的手机号到文件? (y/n): ")
                if save_phones.lower() == 'y':
                    phone_filename = input("请输入手机号文件名（默认为 phone_numbers.txt）: ") or "phone_numbers.txt"
                    with open(phone_filename, 'w', encoding='utf-8') as f:
                        for phone in phone_numbers:
                            f.write(phone + '\n')
                    print(f"手机号已保存为: {os.path.abspath(phone_filename)}")
        
        return cleaned_text, phone_numbers
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return None, None

def main():
    """主函数"""
    print("文本数据清理与手机号提取工具")
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