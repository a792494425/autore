#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SiliconFlow手机号填写工具 - 单浏览器顺序版
功能：一次只打开一个浏览器，等待用户关闭当前浏览器后再打开下一个
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random
import os
import re
import sys

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
    从完全清理后的文本中提取手机号（逐字符扫描方法）
    
    参数:
        text (str): 已清理的文本（无空白字符）
    
    返回:
        list: 提取到的手机号列表
    """
    # 存储找到的手机号
    found_phones = []
    
    # 逐字符扫描文本
    i = 0
    while i <= len(text) - 11:  # 需要至少11个字符才能形成手机号
        # 检查当前位置开始的11个字符是否是手机号
        potential_phone = text[i:i+11]
        
        # 检查是否符合中国大陆手机号的格式（1开头的11位数字）
        if potential_phone[0] == '1' and potential_phone.isdigit():
            # 进一步验证第二位是否在3-9之间
            if '3' <= potential_phone[1] <= '9':
                found_phones.append(potential_phone)
                print(f"在位置 {i} 找到手机号: {potential_phone}")
                
                # 跳过这个手机号的剩余部分
                i += 11
                continue
        
        # 移动到下一个字符
        i += 1
    
    # 去除重复的手机号
    unique_phones = list(set(found_phones))
    return unique_phones

def fill_phone_number(phone_number, index, total):
    """
    打开一个浏览器并填写手机号，等待用户关闭后返回
    
    参数:
        phone_number (str): 要填写的手机号
        index (int): 当前处理的索引
        total (int): 总共需要处理的手机号数量
        
    返回:
        bool: 是否成功
    """
    # 创建一个临时目录作为用户数据目录
    user_data_dir = f"chrome_user_data_{phone_number}"
    os.makedirs(user_data_dir, exist_ok=True)
    
    # 创建独立的chromedriver目录
    driver_dir = f"chromedriver_dir_{phone_number}"
    os.makedirs(driver_dir, exist_ok=True)
    
    print(f"\n[{index}/{total}] 正在为手机号 {phone_number} 启动浏览器...")
    
    try:
        # Chrome选项
        options = uc.ChromeOptions()
        
        # 添加用户代理
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.143 Safari/537.36")
        
        # 设置用户数据目录
        options.add_argument(f"--user-data-dir={os.path.abspath(user_data_dir)}")
        
        # 基本设置
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 初始化浏览器
        driver = uc.Chrome(
            options=options,
            driver_executable_path=None,
            headless=False,
            version_main=133,
            use_subprocess=True,
            cache_path=os.path.abspath(driver_dir)
        )
        
        # 设置隐式等待
        driver.implicitly_wait(10)
        
        # 打开登录页面
        url = "https://account.siliconflow.cn/zh/login?redirect=https%3A%2F%2Fcloud.siliconflow.cn%2F%3F"
        driver.get(url)
        print(f"[{index}/{total}] 已打开登录页面")
        
        # 等待页面加载
        time.sleep(2)
        
        # 尝试找到并填写手机号输入框
        selectors = [
            "//input[@placeholder='请输入手机号' or contains(@placeholder, '手机号')]",
            "//input[contains(@class, 'phone') or contains(@name, 'phone') or contains(@id, 'phone')]",
            "//input[@type='tel']"
        ]
        
        phone_input = None
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    phone_input = elements[0]
                    break
            except:
                continue
        
        if phone_input:
            # 点击输入框
            phone_input.click()
            
            # 清空输入框
            phone_input.clear()
            
            # 输入手机号
            phone_input.send_keys(phone_number)
            print(f"[{index}/{total}] 已成功填写手机号: {phone_number}")
            
            # 尝试点击复选框
            try:
                # 查找复选框
                checkbox_selectors = [
                    "//input[@class='ant-checkbox-input' and @type='checkbox']",
                    "//span[contains(@class, 'ant-checkbox')]/input[@type='checkbox']",
                    "//input[@type='checkbox']",
                    "//label[contains(@class, 'ant-checkbox-wrapper')]//input"
                ]
                
                for selector in checkbox_selectors:
                    checkbox_elements = driver.find_elements(By.XPATH, selector)
                    if checkbox_elements:
                        action = ActionChains(driver)
                        action.move_to_element(checkbox_elements[0]).click().perform()
                        print(f"[{index}/{total}] 已点击复选框")
                        break
            except Exception as e:
                print(f"[{index}/{total}] 点击复选框时出错: {e}")
            
            # 查找获取验证码按钮
            try:
                code_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '验证码') or contains(text(), '获取')]")
                if code_buttons:
                    action = ActionChains(driver)
                    action.move_to_element(code_buttons[0]).perform()
                    print(f"[{index}/{total}] 已找到获取验证码按钮，等待手动点击")
            except:
                pass
                
        else:
            print(f"[{index}/{total}] 未找到手机号输入框")
        
        print(f"\n[{index}/{total}] 浏览器已准备就绪，正在处理手机号: {phone_number}")
        
        if index < total:
            next_index = index + 1
            next_phone = phone_numbers[next_index - 1]
            print(f"请在完成当前操作后关闭浏览器窗口")
            print(f"下一个要处理的是第 {next_index}/{total} 个手机号: {next_phone}")
        else:
            print(f"这是最后一个手机号，处理完成后关闭浏览器即可结束")
        
        # 等待浏览器被关闭
        is_closed = False
        check_count = 0
        max_checks = 300  # 最多等待10分钟 (300 * 2秒)
        
        while not is_closed and check_count < max_checks:
            try:
                # 简单的检查，尝试获取标题
                title = driver.title
                time.sleep(2)  # 每2秒检查一次
                check_count += 1
            except Exception:
                print(f"[{index}/{total}] 检测到浏览器已关闭")
                is_closed = True
                break
        
        if not is_closed:
            print(f"[{index}/{total}] 等待超时，强制关闭浏览器")
            try:
                driver.quit()
            except:
                pass
        
        return True
                
    except Exception as e:
        print(f"[{index}/{total}] 发生错误: {e}")
        return False

if __name__ == "__main__":
    print("SiliconFlow手机号填写工具 - 单浏览器顺序版")
    print("=" * 50)
    print("请输入或粘贴包含手机号的文本")
    print("输入完成后，请键入'END'然后按回车结束输入")
    print("系统将依次为每个手机号打开浏览器，关闭当前浏览器后将自动打开下一个")
    print("=" * 50)
    
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
    
    # 合并所有输入行
    input_text = "\n".join(lines)
    
    # 显示原始文本
    print("\n您输入的原始文本是：")
    print("-" * 50)
    print(input_text)
    print("-" * 50)
    print(f"原始文本长度: {len(input_text)} 字符")
    print(f"原始文本行数: {len(lines)} 行")
    
    # 清理文本（去除所有空格和换行）
    cleaned_text = clean_text(input_text)
    print(f"\n清理后的文本长度: {len(cleaned_text)} 字符")
    print("所有空格、换行和空白字符已移除")
    
    # 从清理后的文本中提取手机号
    phone_numbers = extract_phone_numbers(cleaned_text)
    
    # 检查是否找到手机号
    if not phone_numbers:
        print("未在输入文本中找到有效的手机号！")
        sys.exit(1)
    
    # 显示找到的手机号
    print(f"\n成功提取到 {len(phone_numbers)} 个手机号:")
    for i, phone in enumerate(phone_numbers):
        print(f"{i+1}. {phone}")
    
    # 询问用户是否继续
    confirm = input(f"\n是否依次为这 {len(phone_numbers)} 个手机号启动浏览器? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消操作。")
        sys.exit(0)
    
    # 顺序处理每个手机号
    total_phones = len(phone_numbers)
    print(f"\n准备依次处理 {total_phones} 个手机号...")
    
    completed = 0
    for i, phone in enumerate(phone_numbers):
        current_index = i + 1
        print(f"\n处理第 {current_index}/{total_phones} 个手机号: {phone}")
        
        # 填写手机号
        success = fill_phone_number(phone, current_index, total_phones)
        
        if success:
            completed += 1
            print(f"已完成 {completed}/{total_phones} 个手机号")
        else:
            print(f"处理手机号 {phone} 时出错，跳过")
        
        # 在每个手机号处理完后显示进度
        remaining = total_phones - completed
        if remaining > 0:
            print(f"\n还剩 {remaining} 个手机号等待处理")
    
    print(f"\n所有 {total_phones} 个手机号已处理完毕!")
    print("感谢使用!") 