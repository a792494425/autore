import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import threading
import random
import string
import os
import re

# 全局变量存储浏览器驱动实例，防止被垃圾回收
browser_drivers = []

def random_sleep(min_seconds=0.5, max_seconds=2.0):
    """随机睡眠一段时间，模拟人类行为"""
    time.sleep(random.uniform(min_seconds, max_seconds))

# 不再使用人类模拟输入方法
# def human_like_typing(element, text):
#     """模拟人类输入，有随机间隔"""
#     for char in text:
#         element.send_keys(char)
#         # 随机短暂停顿，模拟人类打字速度
#         time.sleep(random.uniform(0.05, 0.25))

def preprocess_text(text):
    """
    预处理文本，去除空行并格式化数据
    
    参数:
        text (str): 原始文本
        
    返回:
        str: 处理后的文本
    """
    # 按行分割文本
    lines = text.split('\n')
    
    # 过滤掉空行和只包含空白字符的行
    non_empty_lines = [line for line in lines if line.strip()]
    
    # 打印处理结果
    print(f"原始文本行数: {len(lines)}")
    print(f"去除空行后的行数: {len(non_empty_lines)}")
    
    # 将非空行重新组合为文本
    processed_text = '\n'.join(non_empty_lines)
    
    return processed_text

def auto_fill_phone(phone_number):
    """
    自动打开SiliconFlow登录页面并填写手机号
    
    参数:
        phone_number (str): 要填写的手机号码
    """
    global browser_drivers
    
    print(f"开始为手机号 {phone_number} 自动填写表单...")
    
    # 创建一个临时目录作为用户数据目录，每次使用不同的目录以隔离会话
    user_data_dir = f"chrome_user_data_{phone_number}"
    
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
        
        # 增加随机性，避免指纹追踪
        options.add_argument(f"--window-size={random.randint(1000, 1920)},{random.randint(700, 1080)}")
        
        # 增加会话隐私性
        options.add_argument("--incognito")
        
        # 禁用自动化扩展
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 初始化undetected_chromedriver，强制使用与当前Chrome版本兼容的驱动
        driver = uc.Chrome(
            options=options,
            driver_executable_path=None,
            headless=False,
            version_main=133,  # 固定使用Chrome 133版本的驱动
            use_subprocess=True,  # 使用子进程运行，提高稳定性
        )
        
        # 将驱动实例添加到全局列表中，防止被垃圾回收
        browser_drivers.append(driver)
        
        # 设置隐式等待
        driver.implicitly_wait(10)
        
        # 打开登录页面
        url = "https://account.siliconflow.cn/zh/login?redirect=https%3A%2F%2Fcloud.siliconflow.cn%2F%3F"
        driver.get(url)
        print(f"已为手机号 {phone_number} 打开登录页面")
        
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
                print("未找到手机号输入框，尝试查看页面源码...")
                print(driver.page_source)
                return
            
            # 直接点击输入框
            phone_input.click()
            
            # 清空输入框
            phone_input.clear()
            
            # 直接输入手机号，不再模拟人类输入
            phone_input.send_keys(phone_number)
            
            print(f"已成功填写手机号: {phone_number}")
            
            # 可能的后续操作，如按下Tab键或点击获取验证码
            if random.choice([True, False]):
                action = ActionChains(driver)
                action.send_keys(Keys.TAB).perform()
            else:
                # 尝试查找并点击验证码按钮，但不强制
                try:
                    code_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '验证码') or contains(text(), '获取')]")
                    if code_buttons:
                        # 鼠标移动到按钮
                        action = ActionChains(driver)
                        action.move_to_element(code_buttons[0]).perform()
                except:
                    pass
            
        except Exception as e:
            print(f"填写手机号时出错: {e}")
            
            # 如果上面的方法失败，可以尝试打印页面源代码帮助调试
            print("页面源代码:")
            print(driver.page_source)
            
    except Exception as e:
        print(f"浏览器操作出错: {e}")
        
    print(f"手机号 {phone_number} 脚本执行完毕")
    # 注意：不要在这里调用driver.quit()，保持浏览器打开

def open_multiple_browsers(phone_numbers):
    """
    同时打开多个浏览器实例并填写不同的手机号
    
    参数:
        phone_numbers (list): 要填写的手机号列表
    """
    threads = []
    
    # 为每个手机号创建一个线程
    for phone in phone_numbers:
        thread = threading.Thread(target=auto_fill_phone, args=(phone,))
        thread.daemon = False  # 设置为非守护线程
        threads.append(thread)
    
    # 启动所有线程
    for thread in threads:
        thread.start()
        # 每个浏览器启动间隔随机延迟，更像人类行为
        random_sleep(2.0, 3.0)
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("所有浏览器实例已启动并填写完毕")

def extract_phone_numbers(text):
    """
    从提供的文本中提取手机号 - 先预处理文本，然后使用逐字符扫描方式提取所有可能的11位手机号
    
    参数:
        text (str): 包含手机号的文本
        
    返回:
        list: 提取到的手机号列表
    """
    # 预处理文本 - 去除空行
    processed_text = preprocess_text(text)
    
    print("\n开始扫描文本中的手机号...")
    
    # 首先移除文本中所有的空白字符（空格、制表符、换行符等）
    # 这样就不会因为空格或格式问题而导致手机号识别失败
    clean_text = ''.join(processed_text.split())
    print(f"清理后的文本长度: {len(clean_text)} 字符")
    
    # 存储找到的手机号
    found_phones = []
    
    # 逐字符扫描文本
    i = 0
    while i <= len(clean_text) - 11:  # 需要至少11个字符才能形成手机号
        # 检查当前位置开始的11个字符是否是手机号
        potential_phone = clean_text[i:i+11]
        
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
    
    # 最终结果
    print(f"\n通过扫描找到 {len(unique_phones)} 个唯一手机号: {unique_phones}")
    
    # 备用方法：如果扫描方法没有找到任何手机号，尝试直接使用正则表达式
    if not unique_phones:
        print("扫描方法未找到手机号，尝试使用正则表达式...")
        # 直接使用正则表达式查找所有1开头的11位数字
        regex_phones = re.findall(r'1[3-9]\d{9}', text)
        if regex_phones:
            unique_phones = list(set(regex_phones))
            print(f"通过正则表达式找到 {len(unique_phones)} 个手机号: {unique_phones}")
    
    return unique_phones

def extract_phone_from_line(line):
    """
    从单行文本中提取手机号
    
    参数:
        line (str): 一行文本
    
    返回:
        str 或 None: 提取到的手机号，如果没找到则返回None
    """
    # 如果是空行，直接返回None
    if not line.strip():
        return None
    
    # 将行按照多种分隔符分割
    parts = re.split(r'\t|\s{2,}|\s+', line.strip())
    
    # 检查是否有足够的部分，如果第6部分是手机号
    if len(parts) >= 6:
        potential_phone = parts[5]
        if re.match(r'^1[3-9]\d{9}$', potential_phone):
            return potential_phone
    
    # 如果没找到，尝试使用正则表达式
    matches = re.findall(r'1[3-9]\d{9}', line)
    if matches:
        return matches[0]
    
    return None

def process_special_format(text):
    """
    专门处理用户提供的特定格式数据，直接提取第6列的手机号
    
    参数:
        text (str): 特定格式的文本
        
    返回:
        list: 提取到的手机号列表
    """
    # 预处理 - 去除空行
    processed_text = preprocess_text(text)
    
    # 存储找到的手机号
    phone_numbers = []
    
    # 按行处理
    for line in processed_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 拆分行 - 使用多种分隔符
        parts = re.split(r'\t|\s{2,}|\s+', line.strip())
        
        # 检查是否有足够的字段
        if len(parts) >= 6:
            # 第6个字段应该是手机号
            potential_phone = parts[5]
            
            # 验证手机号格式
            if re.match(r'^1[3-9]\d{9}$', potential_phone):
                phone_numbers.append(potential_phone)
                print(f"从行 '{line}' 提取到手机号: {potential_phone}")
    
    # 去重
    unique_phones = list(set(phone_numbers))
    
    print(f"使用特定格式处理方法共找到 {len(unique_phones)} 个手机号: {unique_phones}")
    
    # 如果特定格式处理方法失败，回退到普通提取方法
    if not unique_phones:
        print("特定格式处理方法未找到手机号，尝试使用通用方法...")
        unique_phones = extract_phone_numbers(text)
    
    return unique_phones

if __name__ == "__main__":
    print("手机号批量填写工具")
    print("请粘贴包含手机号的文本，我们会在您输入的过程中提取手机号")
    print("每输入一行后按回车，输入空行结束(按两次回车)")
    
    # 实时处理用户输入并提取手机号
    phone_numbers = []
    buffer = []  # 保存尚未处理的行
    
    print("\n请开始输入数据（每行按回车，空行结束）:")
    while True:
        line = input()
        
        # 如果是空行，结束输入
        if not line:
            # 处理缓冲区中的剩余数据
            if buffer:
                remaining_text = '\n'.join(buffer)
                remaining_phones = process_special_format(remaining_text)
                for phone in remaining_phones:
                    if phone not in phone_numbers:
                        phone_numbers.append(phone)
                buffer = []
            break
        
        # 添加当前行到缓冲区
        buffer.append(line)
        
        # 实时提取当前行的手机号
        phone = extract_phone_from_line(line)
        if phone and phone not in phone_numbers:
            phone_numbers.append(phone)
            print(f"从输入中提取到手机号: {phone}")
            
        # 每积累5行，处理一次缓冲区
        if len(buffer) >= 5:
            buffer_text = '\n'.join(buffer)
            buffer_phones = process_special_format(buffer_text)
            for phone in buffer_phones:
                if phone not in phone_numbers:
                    phone_numbers.append(phone)
            buffer = []
    
    # 检查是否找到手机号
    if not phone_numbers:
        print("未在输入文本中找到有效的手机号！")
        exit(1)
    
    # 显示找到的所有手机号
    print(f"\n成功提取到 {len(phone_numbers)} 个手机号:")
    for i, phone in enumerate(phone_numbers):
        print(f"{i+1}. {phone}")
    
    # 询问用户是否继续
    confirm = input("\n是否使用这些手机号启动浏览器? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消操作。")
        exit(0)
    
    # 直接运行，不再进行确认
    print(f"\n正在启动 {len(phone_numbers)} 个浏览器并填写手机号...")
    open_multiple_browsers(phone_numbers)
    
    # 重要：保持脚本运行，防止浏览器关闭
    print("\n所有操作已完成。浏览器将保持打开状态。")
    print("请按Ctrl+C手动终止此脚本（当您使用完浏览器后）...")
    
    # 无限循环保持脚本运行
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("\n脚本已终止，感谢使用！") 