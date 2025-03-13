import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import multiprocessing
import random
import string
import os
import re
import uuid
import sys
import requests
import json

def random_sleep(min_seconds=0.5, max_seconds=2.0):
    """随机睡眠一段时间，模拟人类行为"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def clean_text(text):
    """
    去除文本中的所有空白字符（空格、制表符、换行符等）
    
    参数:
        text (str): 原始文本
    
    返回:
        str: 清理后的纯文本（不包含任何空白字符）
    """
    return ''.join(text.split())

def get_verification_code(phone_number, process_id, sid="87264"):
    """
    通过API获取手机验证码
    
    参数:
        phone_number (str): 手机号码
        process_id (str): 进程ID
        sid (str): 项目ID，默认为87264
    
    返回:
        str: 验证码，如果获取失败则返回None
    """
    # API信息
    api_url = "https://api.haozhuma.cn/sms/"
    token = "12979f4ebab7cfff72c6f716a31256b673a61cb5eb74b6f000d82cbd5c1d833f7ce230aa25526a061c921eed962625876572a81c2e15f0b4a7b497091f5fb39ce355c9f42ef1ba7f5c8bf129a16585b7"
    
    # 构建请求参数
    params = {
        "api": "getMessage",
        "token": token,
        "sid": sid,
        "phone": phone_number
    }
    
    try:
        print(f"[进程 {process_id}] 正在为手机号 {phone_number} 获取验证码...")
        response = requests.get(api_url, params=params)
        response_data = response.json()
        
        # 检查响应状态
        if response_data.get("code") == "0":
            verification_code = response_data.get("yzm")
            print(f"[进程 {process_id}] 成功获取验证码: {verification_code}")
            return verification_code
        else:
            print(f"[进程 {process_id}] 获取验证码失败: {response_data.get('msg')}")
            return None
    except Exception as e:
        print(f"[进程 {process_id}] 获取验证码时出错: {e}")
        return None

def auto_fill_phone(phone_number, process_id, sid="87264"):
    """
    自动打开SiliconFlow登录页面并填写手机号
    
    参数:
        phone_number (str): 要填写的手机号码
        process_id (str): 进程唯一标识符
        sid (str): 验证码API的项目ID，默认为87264
    """    
    print(f"[进程 {process_id}] 开始为手机号 {phone_number} 自动填写表单...")
    
    # 创建一个临时目录作为用户数据目录，每次使用不同的目录以隔离会话
    user_data_dir = f"chrome_user_data_{phone_number}_{process_id}"
    
    # 确保目录存在
    os.makedirs(user_data_dir, exist_ok=True)
    
    try:
        # 使用undetected_chromedriver而不是标准selenium
        options = uc.ChromeOptions()
        
        # 添加随机用户代理
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.143 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.143 Safari/537.36 Edg/120.0.0.0"
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # 设置用户数据目录
        options.add_argument(f"--user-data-dir={os.path.abspath(user_data_dir)}")
        
        # 设置首次运行参数，避免显示首次运行对话框
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-sandbox")
        
        # 增加随机性，避免指纹追踪
        window_width = random.randint(1000, 1920)
        window_height = random.randint(700, 1080)
        options.add_argument(f"--window-size={window_width},{window_height}")
        
        # 设置窗口位置，尽量避免重叠
        position_x = random.randint(0, 200) + (int(process_id) % 5) * 100
        position_y = random.randint(0, 100) + (int(process_id) % 3) * 100
        options.add_argument(f"--window-position={position_x},{position_y}")
        
        # 增加会话隐私性
        options.add_argument("--incognito")
        
        # 禁用自动化扩展
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 确保每个浏览器的端口不同
        debug_port = 9000 + int(process_id) % 1000
        options.add_argument(f"--remote-debugging-port={debug_port}")
        
        # 禁用扩展和GPU，提高稳定性
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        
        # 初始化undetected_chromedriver，强制使用与当前Chrome版本兼容的驱动
        driver = uc.Chrome(
            options=options,
            driver_executable_path=None,
            headless=False,
            version_main=133,  # 固定使用Chrome 133版本的驱动
            use_subprocess=True,  # 使用子进程运行，提高稳定性
        )
        
        # 设置隐式等待
        driver.implicitly_wait(10)
        
        # 打开登录页面
        url = "https://account.siliconflow.cn/zh/login?redirect=https%3A%2F%2Fcloud.siliconflow.cn%2F%3F"
        driver.get(url)
        print(f"[进程 {process_id}] 已为手机号 {phone_number} 打开登录页面")
        
        # 随机延迟，模拟人类阅读页面
        random_sleep(1.0, 2.0)
        
        # 尝试找到并填写手机号输入框
        try:
            # 尝试通过各种选择器找到输入框
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
            
            if not phone_input:
                print(f"[进程 {process_id}] 未找到手机号输入框，尝试查看页面源码...")
                print(driver.page_source)
                return
            
            # 直接点击输入框
            phone_input.click()
            
            # 清空输入框
            phone_input.clear()
            
            # 直接输入手机号，不再模拟人类输入
            phone_input.send_keys(phone_number)
            
            print(f"[进程 {process_id}] 已成功填写手机号: {phone_number}")
            
            # 尝试找到并点击复选框
            random_sleep(0.5, 1.0)
            
            try:
                # 使用多种选择器尝试找到复选框
                checkbox_selectors = [
                    "//input[@class='ant-checkbox-input' and @type='checkbox']",
                    "//span[contains(@class, 'ant-checkbox')]/input[@type='checkbox']",
                    "//input[@type='checkbox']",
                    "//label[contains(@class, 'ant-checkbox-wrapper')]//input"
                ]
                
                checkbox = None
                for selector in checkbox_selectors:
                    try:
                        checkbox_elements = driver.find_elements(By.XPATH, selector)
                        if checkbox_elements:
                            checkbox = checkbox_elements[0]
                            break
                    except:
                        continue
                
                if checkbox:
                    # 创建动作链
                    action = ActionChains(driver)
                    # 移动到复选框并点击
                    action.move_to_element(checkbox).click().perform()
                    print(f"[进程 {process_id}] 已点击复选框")
                    random_sleep(0.5, 1.0)
                else:
                    # 如果没有找到复选框，尝试点击复选框的父元素
                    try:
                        checkbox_containers = driver.find_elements(By.XPATH, "//span[contains(@class, 'ant-checkbox')]")
                        if checkbox_containers:
                            action = ActionChains(driver)
                            action.move_to_element(checkbox_containers[0]).click().perform()
                            print(f"[进程 {process_id}] 已点击复选框容器")
                            random_sleep(0.5, 1.0)
                        else:
                            print(f"[进程 {process_id}] 未找到复选框元素")
                    except Exception as e:
                        print(f"[进程 {process_id}] 点击复选框容器时出错: {e}")
            except Exception as e:
                print(f"[进程 {process_id}] 尝试尝试点击复选框时出错: {e}")
            
            # 尝试点击获取验证码按钮并自动填写验证码
            try:
                # 查找并点击获取验证码按钮，基于用户提供的HTML结构
                code_button_selectors = [
                    # 基于用户提供的按钮结构
                    "//button[contains(@class, 'ant-btn') and contains(@class, 'ant-btn-link')]/span[text()='获取验证码']/parent::button",
                    "//button[contains(@class, 'ant-btn')]/span[text()='获取验证码']/parent::button",
                    "//button[@type='button' and contains(@class, 'ant-btn')]/span[contains(text(), '获取验证码')]/parent::button",
                    # 原有的选择器作为备用
                    "//button[contains(text(), '验证码') or contains(text(), '获取')]",
                    "//span[contains(text(), '验证码')]/parent::button",
                    "//div[contains(text(), '验证码')]/parent::button"
                ]
                
                code_button = None
                for selector in code_button_selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        if elements:
                            code_button = elements[0]
                            print(f"[进程 {process_id}] 已找到验证码按钮: {selector}")
                            break
                    except Exception as e:
                        continue
                
                if code_button:
                    # 确保按钮可见并可点击
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, code_button_selectors[0]))
                    )
                    
                    # JavaScript点击可能更可靠，尤其是对于React渲染的元素
                    try:
                        driver.execute_script("arguments[0].click();", code_button)
                        print(f"[进程 {process_id}] 已使用JavaScript点击获取验证码按钮")
                    except Exception as js_error:
                        # 如果JavaScript点击失败，尝试使用常规点击
                        print(f"[进程 {process_id}] JavaScript点击失败，尝试常规点击: {js_error}")
                        action = ActionChains(driver)
                        action.move_to_element(code_button).click().perform()
                    
                    print(f"[进程 {process_id}] 已点击获取验证码按钮")
                    
                    # 等待一定时间，以便验证码能够发送
                    random_sleep(3.0, 5.0)
                    
                    # 通过API获取验证码
                    verification_code = get_verification_code(phone_number, process_id, sid)
                    
                    if verification_code:
                        # 查找验证码输入框
                        code_input_selectors = [
                            "//input[contains(@placeholder, '验证码')]",
                            "//input[contains(@class, 'code') or contains(@name, 'code') or contains(@id, 'code')]"
                        ]
                        
                        code_input = None
                        for selector in code_input_selectors:
                            code_inputs = driver.find_elements(By.XPATH, selector)
                            if code_inputs:
                                code_input = code_inputs[0]
                                break
                        
                        if code_input:
                            # 输入验证码
                            code_input.click()
                            code_input.clear()
                            for digit in verification_code:
                                code_input.send_keys(digit)
                                random_sleep(0.1, 0.3)
                            
                            print(f"[进程 {process_id}] 已输入验证码: {verification_code}")
                            
                            # 尝试查找并点击登录/提交按钮
                            submit_button_selectors = [
                                "//button[contains(@type, 'submit')]",
                                "//button[contains(text(), '登录') or contains(text(), '注册') or contains(text(), '提交')]",
                                "//div[contains(text(), '登录')]/parent::button",
                                "//span[contains(text(), '登录')]/parent::button"
                            ]
                            
                            submit_button = None
                            for selector in submit_button_selectors:
                                submit_buttons = driver.find_elements(By.XPATH, selector)
                                if submit_buttons:
                                    submit_button = submit_buttons[0]
                                    break
                            
                            if submit_button:
                                random_sleep(1.0, 2.0)
                                action = ActionChains(driver)
                                action.move_to_element(submit_button).click().perform()
                                print(f"[进程 {process_id}] 已点击登录/提交按钮")
                            else:
                                print(f"[进程 {process_id}] 未找到登录/提交按钮")
                        else:
                            print(f"[进程 {process_id}] 未找到验证码输入框")
                    else:
                        print(f"[进程 {process_id}] 未能获取验证码")
                else:
                    print(f"[进程 {process_id}] 未找到获取验证码按钮，尝试打印页面元素...")
                    # 打印页面上所有按钮的HTML，帮助调试
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    print(f"[进程 {process_id}] 页面上找到 {len(buttons)} 个按钮元素:")
                    for i, btn in enumerate(buttons):
                        try:
                            btn_html = btn.get_attribute("outerHTML")
                            btn_text = btn.text
                            print(f"按钮 {i+1}: {btn_text} - HTML: {btn_html}")
                        except:
                            pass
            except Exception as e:
                print(f"[进程 {process_id}] 处理验证码时出错: {e}")
                
        except Exception as e:
            print(f"[进程 {process_id}] 填写手机号时出错: {e}")
            
            # 如果上面的方法失败，可以尝试打印页面源代码帮助调试
            print(f"[进程 {process_id}] 页面源代码:")
            print(driver.page_source)
            
    except Exception as e:
        print(f"[进程 {process_id}] 浏览器操作出错: {e}")
        
    print(f"[进程 {process_id}] 手机号 {phone_number} 脚本执行完毕")
    
    # 保持进程运行，不关闭浏览器
    while True:
        try:
            time.sleep(1000)
        except KeyboardInterrupt:
            print(f"[进程 {process_id}] 接收到终止信号")
            break

def open_multiple_browsers(phone_numbers, sid="87264"):
    """
    使用多进程打开多个浏览器实例并填写不同的手机号
    
    参数:
        phone_numbers (list): 要填写的手机号列表
        sid (str): 验证码API的项目ID，默认为87264
    """
    processes = []
    
    # 为每个手机号创建一个进程
    for i, phone in enumerate(phone_numbers):
        # 为每个进程分配一个ID
        process_id = str(i + 1)
        
        # 创建进程
        process = multiprocessing.Process(
            target=auto_fill_phone, 
            args=(phone, process_id, sid)
        )
        
        processes.append(process)
    
    # 启动所有进程
    for i, process in enumerate(processes):
        print(f"正在启动第 {i+1}/{len(processes)} 个浏览器实例...")
        process.start()
        # 每个浏览器启动间隔随机延迟
        time.sleep(random.uniform(5.0, 8.0))
    
    print(f"已启动 {len(processes)} 个浏览器进程")
    return processes

def extract_phone_numbers_from_clean_text(text):
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

if __name__ == "__main__":
    # 确保脚本使用多进程模式启动
    multiprocessing.freeze_support()
    
    print("SiliconFlow手机号自动填写工具 (多进程版)")
    print("=" * 50)
    print("请输入或粘贴包含手机号的文本")
    print("输入完成后，请键入'END'然后按回车结束输入")
    print("这样可以确保处理所有数据，即使其中包含空行")
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
    phone_numbers = extract_phone_numbers_from_clean_text(cleaned_text)
    
    # 检查是否找到手机号
    if not phone_numbers:
        print("未在输入文本中找到有效的手机号！")
        sys.exit(1)
    
    # 显示找到的手机号
    print(f"\n成功提取到 {len(phone_numbers)} 个手机号:")
    for i, phone in enumerate(phone_numbers):
        print(f"{i+1}. {phone}")
    
    # 项目ID已设置为固定值87264
    sid = "87264"
    print(f"\n验证码API的项目ID(sid)已设置为: {sid}")
    
    # 询问用户是否继续
    confirm = input(f"\n是否为这 {len(phone_numbers)} 个手机号启动浏览器? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消操作。")
        sys.exit(0)
    
    # 打开多个浏览器
    print(f"\n正在为 {len(phone_numbers)} 个手机号启动独立的浏览器进程...")
    processes = open_multiple_browsers(phone_numbers, sid)
    
    # 输出提示信息
    print("\n所有浏览器已启动完成，每个浏览器在独立的进程中运行")
    print("这些浏览器会一直保持运行，直到您手动关闭它们")
    print("您可以按Ctrl+C终止此脚本，浏览器仍会保持运行")
    print("或者您可以直接关闭浏览器窗口")
    
    # 等待用户手动终止
    try:
        # 主进程保持运行，但不阻塞浏览器进程
        while True:
            time.sleep(60)
            # 检查子进程状态，更新存活进程数
            running_processes = [p for p in processes if p.is_alive()]
            if len(running_processes) < len(processes):
                print(f"当前有 {len(running_processes)}/{len(processes)} 个浏览器进程在运行")
                processes = running_processes
                
            if not running_processes:
                print("所有浏览器进程已关闭，脚本结束")
                break
    except KeyboardInterrupt:
        print("\n主脚本已终止，但浏览器进程会继续运行")
        print("感谢使用！") 