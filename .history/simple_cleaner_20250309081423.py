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
    print("请输入或粘贴要处理的文本（输入完成后按两次回车结束）：")
    
    # 收集输入
    lines = []
    while True:
        try:
            line = input()
            if not line and not lines:  # 跳过开头的空行
                continue
            if not line:  # 结束输入
                break
            lines.append(line)
        except EOFError:  # 处理EOF（Ctrl+D/Ctrl+Z）
            break
    
    # 合并和清理文本
    input_text = "\n".join(lines)
    cleaned_text = clean_text(input_text)
    
    # 显示结果
    print("\n清理后的文本（所有空格和换行已移除）：")
    print("-" * 40)
    print(cleaned_text)
    print("-" * 40)
    print(f"\n原始长度: {len(input_text)} 字符")
    print(f"清理后长度: {len(cleaned_text)} 字符")
    print(f"移除了 {len(input_text) - len(cleaned_text)} 个空白字符") 