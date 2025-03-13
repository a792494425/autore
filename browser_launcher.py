#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
浏览器启动器 - 为每个手机号创建独立的Python脚本并启动
"""

import os
import sys
import re
import time
import random
import subprocess
import platform
import tempfile
import shutil

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

def create_browser_script(phone_number, script_id):
    """
    为指定的手机号创建一个独立的Python脚本
    
    参数:
        phone_number (str): 要填写的手机号
        script_id (int): 脚本ID，用于区分不同的脚本文件
        
    返回:
        str: 创建的脚本文件路径
    """
    # 脚本文件名
    script_name = f"browser_{script_id}_{phone_number}.py"
    
    # 脚本内容模板
    script_content = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自动浏览器实例 - 手机号: {phone_number}
ID: {script_id}
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
import sys
import tempfile
import shutil

# 创建一个临时目录作为用户数据目录
user_data_dir = f"chrome_user_data_{phone_number}_{script_id}"
os.makedirs(user_data_dir, exist_ok=True)

# 创建独立的chromedriver目录
driver_dir = f"chromedriver_dir_{phone_number}_{script_id}"
os.makedirs(driver_dir, exist_ok=True)

# 设置环境变量，使undetected_chromedriver使用自定义目录
os.environ["UC_DRIVER_EXECUTABLE_PATH"] = os.path.join(os.path.abspath(driver_dir), "chromedriver.exe")

# Chrome选项
options = uc.ChromeOptions()

# 添加用户代理
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.143 Safari/537.36")

# 设置用户数据目录
options.add_argument(f"--user-data-dir={{os.path.abspath(user_data_dir)}}")

# 基本设置
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--disable-blink-features=AutomationControlled")

# 设置窗口大小和位置
options.add_argument(f"--window-size={{1000 + (script_id % 5) * 100}},{{800 + (script_id % 3) * 100}}")
options.add_argument(f"--window-position={{50 + script_id * 30}},{{50 + script_id * 20}}")

# 设置随机调试端口
debug_port = 9000 + script_id
options.add_argument(f"--remote-debugging-port={{debug_port}}")

# 打印标识信息
print(f"[实例 {{script_id}}] 正在启动浏览器，填写手机号: {phone_number}")

try:
    # 初始化浏览器 - 使用自定义的cache_path
    driver = uc.Chrome(
        options=options,
        driver_executable_path=None,
        headless=False,
        version_main=133,
        use_subprocess=True,
        browser_executable_path=None,
        user_data_dir=os.path.abspath(user_data_dir),
        cache_path=os.path.abspath(driver_dir)  # 使用独立的缓存目录
    )
    
    # 设置隐式等待
    driver.implicitly_wait(10)
    
    # 打开登录页面
    url = "https://account.siliconflow.cn/zh/login?redirect=https%3A%2F%2Fcloud.siliconflow.cn%2F%3F"
    driver.get(url)
    print(f"[实例 {{script_id}}] 已打开登录页面")
    
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
        phone_input.send_keys("{phone_number}")
        print(f"[实例 {{script_id}}] 已填写手机号: {phone_number}")
        
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
                    print(f"[实例 {{script_id}}] 已点击复选框")
                    break
        except Exception as e:
            print(f"[实例 {{script_id}}] 点击复选框时出错: {{e}}")
        
        # 查找获取验证码按钮
        try:
            code_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '验证码') or contains(text(), '获取')]")
            if code_buttons:
                action = ActionChains(driver)
                action.move_to_element(code_buttons[0]).perform()
                print(f"[实例 {{script_id}}] 已找到获取验证码按钮，等待手动点击")
        except:
            pass
            
    else:
        print(f"[实例 {{script_id}}] 未找到手机号输入框")
    
    print(f"[实例 {{script_id}}] 浏览器已准备就绪，保持运行状态")
    
    # 保持脚本运行
    while True:
        time.sleep(60)
        # 每分钟检查一次浏览器状态
        try:
            # 简单的检查，尝试获取标题
            title = driver.title
        except:
            print(f"[实例 {{script_id}}] 浏览器已关闭，脚本退出")
            break
            
except Exception as e:
    print(f"[实例 {{script_id}}] 发生错误: {{e}}")
finally:
    # 不论成功或失败，都确保清理资源
    print(f"[实例 {{script_id}}] 保持浏览器运行中...")
'''
    
    # 创建脚本文件
    with open(script_name, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 确保文件可执行（Linux/Mac）
    if platform.system() != 'Windows':
        os.chmod(script_name, 0o755)
    
    return script_name

def launch_browsers(phone_numbers):
    """
    为每个手机号启动一个独立的浏览器进程
    
    参数:
        phone_numbers (list): 手机号列表
    """
    processes = []
    
    # 创建共享临时目录
    temp_dir = os.path.join(os.getcwd(), "chrome_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    for i, phone in enumerate(phone_numbers):
        # 创建独立的Python脚本
        script_path = create_browser_script(phone, i+1)
        
        print(f"正在启动第 {i+1}/{len(phone_numbers)} 个浏览器进程...")
        
        # 使用Python解释器运行脚本
        python_executable = sys.executable
        
        # 启动进程
        if platform.system() == 'Windows':
            # Windows下使用start命令启动新窗口
            cmd = f'start "Browser {i+1} - {phone}" {python_executable} {script_path}'
            process = subprocess.Popen(
                cmd,
                shell=True,
                env=dict(os.environ, PYTHONIOENCODING='utf-8')  # 设置环境变量
            )
        else:
            # Linux/Mac下直接启动
            process = subprocess.Popen(
                [python_executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=dict(os.environ, PYTHONIOENCODING='utf-8')  # 设置环境变量
            )
        
        processes.append(process)
        
        # 间隔一段时间启动下一个，给每个进程足够的时间下载和设置chromedriver
        delay = random.uniform(8.0, 12.0)
        print(f"等待 {delay:.1f} 秒后启动下一个浏览器...")
        time.sleep(delay)
    
    print(f"已启动 {len(processes)} 个浏览器进程")
    return processes

if __name__ == "__main__":
    print("SiliconFlow手机号自动填写工具 (多实例版)")
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
    confirm = input(f"\n是否为这 {len(phone_numbers)} 个手机号启动浏览器? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消操作。")
        sys.exit(0)
    
    # 打开多个浏览器
    print(f"\n正在为 {len(phone_numbers)} 个手机号启动独立的浏览器进程...")
    processes = launch_browsers(phone_numbers)
    
    # 输出提示信息
    print("\n所有浏览器已启动完成！每个浏览器在独立的进程中运行")
    print("这些浏览器会一直保持运行，直到您手动关闭它们")
    print("\n你可以在任何时候关闭此控制台窗口，不会影响浏览器运行")
    print("感谢使用！") 