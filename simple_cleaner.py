#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单数据清理脚本
功能：去除文本中的所有空格和换行
"""

def clean_text(text):
    """去除文本中的所有空白字符"""
    return ''.join(text.split())

if __name__ == "__main__":
    print("简单文本清理工具 - 去除所有空格和换行")
    print("=" * 40)
    print("请输入或粘贴要处理的文本")
    print("输入完成后，请键入'END'然后按回车结束输入")
    print("这样可以确保处理所有数据，即使其中包含空行")
    print("=" * 40)
    
    # 收集输入（直到遇到特定结束标记）
    lines = []
    print("请开始输入文本（输入'END'结束）：")
    while True:
        try:
            line = input()
            if line.strip() == "END":  # 使用特定标记结束输入
                break
            lines.append(line)
        except EOFError:  # 处理EOF（Ctrl+D/Ctrl+Z）
            break
    
    # 合并和清理文本
    input_text = "\n".join(lines)
    
    # 显示原始文本，帮助确认所有内容都被读取
    print("\n你输入的原始文本是：")
    print("-" * 40)
    print(input_text)
    print("-" * 40)
    
    # 清理文本
    cleaned_text = clean_text(input_text)
    
    # 显示结果
    print("\n清理后的文本（所有空格和换行已移除）：")
    print("-" * 40)
    print(cleaned_text)
    print("-" * 40)
    print(f"\n原始长度: {len(input_text)} 字符")
    print(f"清理后长度: {len(cleaned_text)} 字符")
    print(f"移除了 {len(input_text) - len(cleaned_text)} 个空白字符")
    
    # 提取并显示找到的手机号
    phone_numbers = []
    i = 0
    while i <= len(cleaned_text) - 11:  # 需要至少11个字符才能形成手机号
        # 检查当前位置开始的11个字符是否是手机号
        potential_phone = cleaned_text[i:i+11]
        
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
    unique_phones = list(set(phone_numbers))
    
    # 显示找到的手机号
    if unique_phones:
        print("\n从清理后的文本中提取到的手机号：")
        for i, phone in enumerate(unique_phones):
            print(f"{i+1}. {phone}")
        print(f"共找到 {len(unique_phones)} 个手机号") 