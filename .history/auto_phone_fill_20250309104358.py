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
    通过API获取手机验证码，持续轮询直到成功获取验证码
    
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
    
    # 设置最大尝试次数和时间限制
    max_attempts = 30  # 最多尝试30次
    retry_interval = 3  # 每次尝试间隔3秒
    total_waited = 0
    max_wait_time = 120  # 最长等待时间为120秒
    
    print(f"[进程 {process_id}] 开始轮询API获取手机号 {phone_number} 的验证码...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            if total_waited >= max_wait_time:
                print(f"[进程 {process_id}] 等待超过{max_wait_time}秒，获取验证码超时")
                return None
            
            print(f"[进程 {process_id}] 第{attempt}次尝试获取验证码，已等待{total_waited}秒...")
            response = requests.get(api_url, params=params)
            response_data = response.json()
            
            print(f"[进程 {process_id}] API响应: {response_data}")
            
            # 检查响应是否包含有效的验证码
            if response_data.get("code") == "0" and response_data.get("yzm"):
                verification_code = response_data.get("yzm")
                print(f"[进程 {process_id}] 成功获取验证码: {verification_code}")
                print(f"[进程 {process_id}] 短信内容: {response_data.get('sms', '无短信内容')}")
                return verification_code
            else:
                print(f"[进程 {process_id}] 尚未收到验证码，错误信息: {response_data.get('msg', '未知错误')}")
                # 等待一段时间后重试
                time.sleep(retry_interval)
                total_waited += retry_interval
        
        except Exception as e:
            print(f"[进程 {process_id}] 获取验证码时出错: {e}")
            time.sleep(retry_interval)
            total_waited += retry_interval
    
    print(f"[进程 {process_id}] 达到最大尝试次数{max_attempts}，获取验证码失败")
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
                # 等待页面充分加载，但减少等待时间
                random_sleep(0.5, 1.0)
                
                print(f"[进程 {process_id}] 开始查找验证码按钮...")
                
                # 优先使用最精确的选择器，减少选择器数量
                code_button_selectors = [
                    # 完全匹配用户提供的HTML结构
                    "//button[@type='button' and contains(@class, 'ant-btn') and contains(@class, 'ant-btn-link')]/span[text()='获取验证码']/parent::button",
                    "//button[contains(@class, 'ant-btn-link')]/span[text()='获取验证码']/parent::button",
                    # 模糊匹配作为备用
                    "//button[contains(@class, 'ant-btn')]/span[contains(text(), '获取验证码')]/parent::button",
                    "//button[contains(text(), '验证码') or contains(text(), '获取')]"
                ]
                
                # 直接查找验证码按钮，跳过其他检查
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
                    # 快速检查按钮是否可点击
                    is_button_disabled = False
                    try:
                        disabled_attr = code_button.get_attribute("disabled")
                        is_button_disabled = disabled_attr == "true" or disabled_attr == "disabled"
                    except:
                        pass
                    
                    if not is_button_disabled:
                        # 直接使用JavaScript点击，这通常是最快的方法
                        try:
                            driver.execute_script("arguments[0].click();", code_button)
                            print(f"[进程 {process_id}] 已点击获取验证码按钮")
                            
                            # 减少等待时间，更快开始获取验证码
                            random_sleep(2.0, 3.0)
                            
                            # 通过API获取验证码
                            verification_code = get_verification_code(phone_number, process_id, sid)
                            
                            if verification_code:
                                # 查找验证码输入框
                                code_input_selectors = [
                                    "//input[contains(@placeholder, '验证码')]",
                                    "//input[contains(@class, 'code') or contains(@name, 'code') or contains(@id, 'code')]",
                                    "//div[contains(text(), '验证码') or contains(text(), '短信')]/following::input[1]",
                                    "//label[contains(text(), '验证码')]/following::input[1]"
                                ]
                                
                                code_input = None
                                for selector in code_input_selectors:
                                    try:
                                        code_inputs = driver.find_elements(By.XPATH, selector)
                                        if code_inputs:
                                            code_input = code_inputs[0]
                                            print(f"[进程 {process_id}] 已找到验证码输入框: {selector}")
                                            break
                                    except Exception as e:
                                        print(f"[进程 {process_id}] 查找验证码输入框出错: {e}")
                                
                                if code_input:
                                    try:
                                        # 输入验证码前先清空输入框
                                        code_input.click()
                                        code_input.clear()
                                        
                                        # 输入验证码，模拟人工输入
                                        print(f"[进程 {process_id}] 开始输入验证码: {verification_code}")
                                        for digit in verification_code:
                                            code_input.send_keys(digit)
                                            random_sleep(0.1, 0.3)
                                        
                                        print(f"[进程 {process_id}] 已输入验证码: {verification_code}")
                                        
                                        # 等待一会，确保验证码被正确接收
                                        random_sleep(1.0, 2.0)
                                        
                                        # 尝试查找并点击登录/提交按钮
                                        submit_button_selectors = [
                                            "//button[contains(@type, 'submit')]",
                                            "//button[contains(text(), '登录') or contains(text(), '注册') or contains(text(), '提交')]",
                                            "//div[contains(text(), '登录')]/parent::button",
                                            "//span[contains(text(), '登录')]/parent::button",
                                            "//button[contains(@class, 'submit') or contains(@class, 'login')]"
                                        ]
                                        
                                        submit_button = None
                                        for selector in submit_button_selectors:
                                            try:
                                                submit_buttons = driver.find_elements(By.XPATH, selector)
                                                if submit_buttons:
                                                    submit_button = submit_buttons[0]
                                                    print(f"[进程 {process_id}] 已找到登录/提交按钮: {selector}")
                                                    break
                                            except Exception as e:
                                                print(f"[进程 {process_id}] 查找登录/提交按钮出错: {e}")
                                        
                                        if submit_button:
                                            random_sleep(1.0, 2.0)
                                            
                                            # 使用JavaScript点击可能更可靠
                                            try:
                                                driver.execute_script("arguments[0].click();", submit_button)
                                                print(f"[进程 {process_id}] 已使用JavaScript点击登录/提交按钮")
                                            except Exception as js_err:
                                                print(f"[进程 {process_id}] JavaScript点击登录按钮失败: {js_err}")
                                                # 如果JavaScript点击失败，尝试常规点击
                                                action = ActionChains(driver)
                                                action.move_to_element(submit_button).click().perform()
                                                print(f"[进程 {process_id}] 已使用ActionChains点击登录/提交按钮")
                                            
                                            print(f"[进程 {process_id}] 登录流程完成")
                                            
                                            # 等待登录成功后的页面加载，确保API密钥菜单可点击
                                            print(f"[进程 {process_id}] 等待页面加载API密钥菜单...")
                                            random_sleep(2.0, 3.0)  # 给足够时间加载菜单
                                            
                                            # 登录成功后执行创建API密钥的操作
                                            try:
                                                print(f"[进程 {process_id}] 开始执行创建API密钥流程...")
                                                
                                                # 使用精确选择器匹配API密钥菜单项，基于用户提供的HTML结构
                                                api_key_menu_selectors = [
                                                    # 精确匹配用户提供的HTML结构
                                                    "//li[contains(@class, 'ant-menu-item') and contains(@data-menu-id, 'account/ak')]",
                                                    "//li[contains(@class, 'ant-menu-item')]//*[contains(text(), 'API') and contains(text(), '密钥')]",
                                                    "//li[contains(@class, 'ant-menu-item')]//svg[contains(@class, 'ant-menu-item-icon')]/parent::li",
                                                    # 通过菜单图标和文本匹配
                                                    "//li[contains(@class, 'ant-menu-item')]//svg/following-sibling::span[contains(text(), 'API')]/parent::li",
                                                    # 通过角色属性匹配
                                                    "//li[@role='menuitem' and contains(., 'API')]",
                                                    # 备用选择器
                                                    "//li[contains(@class, 'ant-menu-item')]"
                                                ]
                                                
                                                # 等待并查找API密钥菜单项
                                                api_key_menu = None
                                                for selector in api_key_menu_selectors:
                                                    try:
                                                        wait = WebDriverWait(driver, 3)
                                                        api_key_menu = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                                                        print(f"[进程 {process_id}] 找到API密钥菜单: {selector}")
                                                        break
                                                    except Exception as e:
                                                        print(f"[进程 {process_id}] 选择器 {selector} 未找到元素")
                                                        continue
                                                
                                                # 如果找到菜单项，尝试多种方式点击它
                                                if api_key_menu:
                                                    click_success = False
                                                    
                                                    # 方法1: 直接JavaScript点击
                                                    try:
                                                        driver.execute_script("arguments[0].click();", api_key_menu)
                                                        print(f"[进程 {process_id}] 已用JavaScript点击API密钥菜单")
                                                        click_success = True
                                                    except Exception as js_error:
                                                        print(f"[进程 {process_id}] JavaScript点击失败: {js_error}")
                                                    
                                                    # 方法2: ActionChains点击
                                                    if not click_success:
                                                        try:
                                                            action = ActionChains(driver)
                                                            action.move_to_element(api_key_menu).click().perform()
                                                            print(f"[进程 {process_id}] 已用ActionChains点击API密钥菜单")
                                                            click_success = True
                                                        except Exception as action_error:
                                                            print(f"[进程 {process_id}] ActionChains点击失败: {action_error}")
                                                    
                                                    # 方法3: 直接点击
                                                    if not click_success:
                                                        try:
                                                            api_key_menu.click()
                                                            print(f"[进程 {process_id}] 已直接点击API密钥菜单")
                                                            click_success = True
                                                        except Exception as direct_error:
                                                            print(f"[进程 {process_id}] 直接点击失败: {direct_error}")
                                                    
                                                    # 方法4: 使用JavaScript导航到API密钥页面
                                                    if not click_success:
                                                        try:
                                                            # 尝试直接导航到API密钥页面
                                                            current_url = driver.current_url
                                                            api_key_url = current_url.split('?')[0].rstrip('/') + "/account/ak"
                                                            driver.get(api_key_url)
                                                            print(f"[进程 {process_id}] 已直接导航到API密钥页面: {api_key_url}")
                                                            click_success = True
                                                        except Exception as nav_error:
                                                            print(f"[进程 {process_id}] 直接导航失败: {nav_error}")
                                                    
                                                    if not click_success:
                                                        print(f"[进程 {process_id}] 所有点击方法都失败，无法访问API密钥页面")
                                                        return
                                                else:
                                                    print(f"[进程 {process_id}] 未找到API密钥菜单项，尝试通过页面结构查找")
                                                    
                                                    # 尝试通过JavaScript查找菜单项
                                                    js_find_menu = """
                                                    (function() {
                                                        // 尝试查找包含API密钥文本的菜单项
                                                        var menuItems = document.querySelectorAll('li, a, div');
                                                        for (var i = 0; i < menuItems.length; i++) {
                                                            var text = menuItems[i].textContent || '';
                                                            if ((text.indexOf('API') >= 0 && text.indexOf('密钥') >= 0) || 
                                                                menuItems[i].innerHTML.indexOf('SVG') >= 0) {
                                                                menuItems[i].click();
                                                                return true;
                                                            }
                                                        }
                                                        
                                                        // 尝试查找左侧菜单中的所有项
                                                        var sideMenuItems = document.querySelectorAll('.ant-menu-item');
                                                        if (sideMenuItems.length > 0) {
                                                            // 尝试点击可能的API密钥菜单项（通常在账户相关菜单中）
                                                                for (var i = 0; i < sideMenuItems.length; i++) {
                                                                    if (sideMenuItems[i].innerHTML.indexOf('svg') >= 0) {
                                                                        sideMenuItems[i].click();
                                                                        return true;
                                                                    }
                                                                }
                                                            }
                                                        return false;
                                                    })();
                                                    """
                                                    try:
                                                        menu_clicked = driver.execute_script(js_find_menu)
                                                        if menu_clicked:
                                                            print(f"[进程 {process_id}] 通过JavaScript成功查找并点击菜单项")
                                                        else:
                                                            print(f"[进程 {process_id}] JavaScript未找到菜单项，尝试直接导航")
                                                            try:
                                                                current_url = driver.current_url
                                                                api_key_url = current_url.split('?')[0].rstrip('/') + "/account/ak"
                                                                driver.get(api_key_url)
                                                                print(f"[进程 {process_id}] 已直接导航到API密钥页面: {api_key_url}")
                                                            except Exception as nav_error:
                                                                print(f"[进程 {process_id}] 导航到API密钥页面失败，无法继续流程")
                                                                return
                                                    except Exception as js_error:
                                                        print(f"[进程 {process_id}] 执行JavaScript查找菜单项时出错: {js_error}")
                                                        return
                                                    
                                                    # 等待API密钥页面加载 - 增加等待时间确保页面完全加载
                                                    print(f"[进程 {process_id}] 等待API密钥页面完全加载...")
                                                    random_sleep(3.0, 5.0)  # 增加等待时间
                                                    
                                                    # 严格按照用户提供的HTML结构搜索"新建 API 密钥"按钮
                                                    print(f"[进程 {process_id}] 尝试使用精确结构查找'新建 API 密钥'按钮...")
                                                    
                                                    # 使用等待机制，确保按钮已加载并可见
                                                    try:
                                                        # 最精确的选择器，完全匹配用户提供的按钮HTML结构
                                                        exact_selector = "//button[@type='button' and contains(@class, 'ant-btn') and contains(@class, 'css-v71kjs') and contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-color-primary') and contains(@class, 'ant-btn-variant-solid')]/span[text()='新建 API 密钥']/parent::button"
                                                        
                                                        # 等待按钮可见和可点击
                                                        wait = WebDriverWait(driver, 10)
                                                        new_api_key_button = wait.until(
                                                            EC.element_to_be_clickable((By.XPATH, exact_selector))
                                                        )
                                                        
                                                        print(f"[进程 {process_id}] 已找到精确匹配的'新建 API 密钥'按钮")
                                                        
                                                        # 使用JavaScript点击按钮以避免其他干扰
                                                        driver.execute_script("arguments[0].scrollIntoView(true);", new_api_key_button)
                                                        driver.execute_script("arguments[0].click();", new_api_key_button)
                                                        print(f"[进程 {process_id}] 已点击'新建 API 密钥'按钮")
                                                        
                                                    except Exception as e:
                                                        # 如果精确选择器失败，尝试更宽松的选择器
                                                        print(f"[进程 {process_id}] 精确选择器未找到按钮: {e}")
                                                        
                                                        try:
                                                            # 使用多个选择器尝试查找按钮
                                                            button_selectors = [
                                                                "//button[contains(@class, 'ant-btn-primary')]/span[text()='新建 API 密钥']/parent::button",
                                                                "//button[contains(@class, 'ant-btn')]/span[text()='新建 API 密钥']/parent::button",
                                                                "//button[contains(@class, 'ant-btn-primary')]/span[contains(text(), '新建')]/parent::button",
                                                                "//button[contains(@class, 'ant-btn-primary')]"
                                                            ]
                                                            
                                                            new_api_key_button = None
                                                            for selector in button_selectors:
                                                                elements = driver.find_elements(By.XPATH, selector)
                                                                if elements:
                                                                    new_api_key_button = elements[0]
                                                                    print(f"[进程 {process_id}] 找到'新建 API 密钥'按钮: {selector}")
                                                                    break
                                                            
                                                            if new_api_key_button:
                                                                # 滚动到按钮并点击
                                                                driver.execute_script("arguments[0].scrollIntoView(true);", new_api_key_button)
                                                                driver.execute_script("arguments[0].click();", new_api_key_button)
                                                                print(f"[进程 {process_id}] 已点击'新建 API 密钥'按钮")
                                                            else:
                                                                # 如果按钮选择器失败，使用JavaScript直接查找和点击
                                                                print(f"[进程 {process_id}] 尝试使用JavaScript直接查找和点击按钮...")
                                                                
                                                                js_click_button = """
                                                                (function() {
                                                                    // 精确匹配文本和样式
                                                                    var buttons = document.querySelectorAll('button');
                                                                    for (var i = 0; i < buttons.length; i++) {
                                                                        if (buttons[i].textContent.trim() === '新建 API 密钥' || 
                                                                            (buttons[i].classList.contains('ant-btn-primary') && 
                                                                             buttons[i].textContent.indexOf('新建') >= 0)) {
                                                                            // 确保按钮可见后点击
                                                                            buttons[i].scrollIntoView();
                                                                            setTimeout(function() { 
                                                                                buttons[i].click();
                                                                            }, 500);
                                                                            return true;
                                                                        }
                                                                    }
                                                                    return false;
                                                                })();
                                                                """
                                                                
                                                                button_clicked = driver.execute_script(js_click_button)
                                                                if button_clicked:
                                                                    print(f"[进程 {process_id}] 已通过JavaScript点击'新建 API 密钥'按钮")
                                                                else:
                                                                    print(f"[进程 {process_id}] 所有方法都无法找到并点击'新建 API 密钥'按钮")
                                                                    # 尝试搜索页面上的所有按钮
                                                                    all_buttons = driver.find_elements(By.TAG_NAME, "button")
                                                                    print(f"[进程 {process_id}] 页面上有 {len(all_buttons)} 个按钮")
                                                                    for i, btn in enumerate(all_buttons):
                                                                        try:
                                                                            btn_text = btn.text
                                                                            btn_html = btn.get_attribute("outerHTML")
                                                                            print(f"按钮 {i}: 文本='{btn_text}', HTML={btn_html}")
                                                                        except:
                                                                            continue
                                                                    
                                                                    return  # 如果找不到按钮，终止流程
                                                            except Exception as find_error:
                                                                print(f"[进程 {process_id}] 查找'新建 API 密钥'按钮时出错: {find_error}")
                                                                return
                                                    
                                                    # 等待模态框出现，增加等待时间
                                                    print(f"[进程 {process_id}] 等待模态框出现...")
                                                    try:
                                                        wait = WebDriverWait(driver, 10)  # 增加等待时间
                                                        modal = wait.until(
                                                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-modal-content')]"))
                                                        )
                                                        print(f"[进程 {process_id}] 模态框已出现")
                                                        
                                                        # 给模态框一点时间完全加载
                                                        random_sleep(1.0, 2.0)
                                                        
                                                        # 在模态框中填写描述
                                                        description_text = f"Auto API Key - {phone_number} - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                                                        
                                                        # 使用精确选择器查找描述输入框
                                                        description_input = wait.until(
                                                            EC.element_to_be_clickable((By.XPATH, "//input[@id='description' and @placeholder='请输入描述信息']"))
                                                        )
                                                        
                                                        # 填写描述
                                                        description_input.click()
                                                        description_input.clear()
                                                        description_input.send_keys(description_text)
                                                        print(f"[进程 {process_id}] 已输入描述: {description_text}")
                                                        
                                                        # 等待描述输入完成
                                                        random_sleep(0.5, 1.0)
                                                        
                                                        # 使用精确选择器查找"新建密钥"按钮
                                                        print(f"[进程 {process_id}] 查找模态框中的'新建密钥'按钮...")
                                                        
                                                        # 点击模态框中的"新建密钥"按钮（基于用户提供的HTML结构）
                                                        modal_button_selectors = [
                                                            # 精确匹配用户提供的按钮
                                                            "//div[contains(@class, 'ant-modal-footer')]/button[contains(@class, 'ant-btn') and contains(@class, 'css-v71kjs') and contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-color-primary') and contains(@class, 'ant-btn-variant-solid')]/span[text()='新建密钥']/parent::button",
                                                            "//div[contains(@class, 'ant-modal-footer')]/button[contains(@class, 'ant-btn-primary')]/span[text()='新建密钥']/parent::button",
                                                            # 模糊匹配
                                                            "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-primary')]",
                                                            "//div[contains(@class, 'ant-modal-content')]//button[contains(@class, 'ant-btn-primary')]",
                                                            "//div[contains(@class, 'ant-modal-footer')]//button[last()]"  # 通常确认按钮是最后一个按钮
                                                        ]
                                                        
                                                        try:
                                                            # 等待按钮可见和可点击
                                                            confirm_button = wait.until(
                                                                EC.element_to_be_clickable((By.XPATH, exact_confirm_selector))
                                                            )
                                                            
                                                            # 滚动到按钮并点击
                                                            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
                                                            driver.execute_script("arguments[0].click();", confirm_button)
                                                            print(f"[进程 {process_id}] 已点击模态框中的'新建密钥'按钮")
                                                            print(f"[进程 {process_id}] API密钥创建流程完成")
                                                            
                                                        except Exception as confirm_error:
                                                            # 尝试使用更宽松的选择器
                                                            print(f"[进程 {process_id}] 精确选择器未找到'新建密钥'按钮: {confirm_error}")
                                                            
                                                            # 使用JavaScript直接查找和点击模态框中的确认按钮
                                                            js_click_confirm = """
                                                            (function() {
                                                                // 查找模态框
                                                                var modal = document.querySelector('.ant-modal-content');
                                                                if (modal) {
                                                                    // 查找底部按钮区域
                                                                    var footer = modal.querySelector('.ant-modal-footer');
                                                                    if (footer) {
                                                                        // 查找所有按钮
                                                                        var buttons = footer.querySelectorAll('button');
                                                                        
                                                                        // 尝试找到"新建密钥"按钮
                                                                        for (var i = 0; i < buttons.length; i++) {
                                                                            if (buttons[i].textContent.indexOf('新建密钥') >= 0 || 
                                                                                (buttons[i].classList.contains('ant-btn-primary') && buttons[i] === buttons[buttons.length-1])) {
                                                                                buttons[i].click();
                                                                                return true;
                                                                            }
                                                                        }
                                                                        
                                                                        // 如果没找到，点击最后一个按钮（通常是确认按钮）
                                                                        if (buttons.length > 0) {
                                                                            buttons[buttons.length - 1].click();
                                                                            return true;
                                                                        }
                                                                    }
                                                                }
                                                                return false;
                                                            })();
                                                            """
                                                            
                                                            confirm_clicked = driver.execute_script(js_click_confirm)
                                                            if confirm_clicked:
                                                                print(f"[进程 {process_id}] 已通过JavaScript点击模态框确认按钮")
                                                                print(f"[进程 {process_id}] API密钥创建流程完成")
                                                            else:
                                                                print(f"[进程 {process_id}] JavaScript未能点击模态框确认按钮")
                                                                
                                                                # 打印模态框中所有按钮，帮助调试
                                                                try:
                                                                    modal_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal-footer')]//button")
                                                                    print(f"[进程 {process_id}] 模态框底部有 {len(modal_buttons)} 个按钮")
                                                                    for i, btn in enumerate(modal_buttons):
                                                                        btn_text = btn.text
                                                                        btn_html = btn.get_attribute("outerHTML")
                                                                        print(f"按钮 {i}: 文本='{btn_text}', HTML={btn_html}")
                                                                except:
                                                                    pass
                                                        except Exception as modal_error:
                                                            print(f"[进程 {process_id}] 处理模态框时出错: {modal_error}")
                                                    except Exception as api_key_error:
                                                        print(f"[进程 {process_id}] 创建API密钥流程出错: {api_key_error}")
                                                else:
                                                    print(f"[进程 {process_id}] 登录流程完成")
                                            except Exception as input_err:
                                                print(f"[进程 {process_id}] 输入验证码时出错: {input_err}")
                                        else:
                                            print(f"[进程 {process_id}] 未找到验证码输入框")
                                else:
                                    print(f"[进程 {process_id}] 未能获取验证码，流程无法继续")
                            except Exception as js_error:
                                # JavaScript点击失败时使用其他方法
                                try:
                                    code_button.click()
                                    print(f"[进程 {process_id}] 已通过直接点击获取验证码按钮")
                                except:
                                    action = ActionChains(driver)
                                    action.move_to_element(code_button).click().perform()
                                    print(f"[进程 {process_id}] 已通过ActionChains点击获取验证码按钮")
                                
                                random_sleep(2.0, 3.0)
                                verification_code = get_verification_code(phone_number, process_id, sid)
                                
                                if verification_code:
                                    # 查找验证码输入框
                                    code_input_selectors = [
                                        "//input[contains(@placeholder, '验证码')]",
                                        "//input[contains(@class, 'code') or contains(@name, 'code') or contains(@id, 'code')]",
                                        "//div[contains(text(), '验证码') or contains(text(), '短信')]/following::input[1]",
                                        "//label[contains(text(), '验证码')]/following::input[1]"
                                    ]
                                    
                                    code_input = None
                                    for selector in code_input_selectors:
                                        try:
                                            code_inputs = driver.find_elements(By.XPATH, selector)
                                            if code_inputs:
                                                code_input = code_inputs[0]
                                                print(f"[进程 {process_id}] 已找到验证码输入框: {selector}")
                                                break
                                        except Exception as e:
                                            print(f"[进程 {process_id}] 查找验证码输入框出错: {e}")
                                    
                                    if code_input:
                                        try:
                                            # 输入验证码前先清空输入框
                                            code_input.click()
                                            code_input.clear()
                                            
                                            # 输入验证码，模拟人工输入
                                            print(f"[进程 {process_id}] 开始输入验证码: {verification_code}")
                                            for digit in verification_code:
                                                code_input.send_keys(digit)
                                                random_sleep(0.1, 0.3)
                                            
                                            print(f"[进程 {process_id}] 已输入验证码: {verification_code}")
                                            
                                            # 等待一会，确保验证码被正确接收
                                            random_sleep(1.0, 2.0)
                                            
                                            # 尝试查找并点击登录/提交按钮
                                            submit_button_selectors = [
                                                "//button[contains(@type, 'submit')]",
                                                "//button[contains(text(), '登录') or contains(text(), '注册') or contains(text(), '提交')]",
                                                "//div[contains(text(), '登录')]/parent::button",
                                                "//span[contains(text(), '登录')]/parent::button",
                                                "//button[contains(@class, 'submit') or contains(@class, 'login')]"
                                            ]
                                            
                                            submit_button = None
                                            for selector in submit_button_selectors:
                                                try:
                                                    submit_buttons = driver.find_elements(By.XPATH, selector)
                                                    if submit_buttons:
                                                        submit_button = submit_buttons[0]
                                                        print(f"[进程 {process_id}] 已找到登录/提交按钮: {selector}")
                                                        break
                                                except Exception as e:
                                                    print(f"[进程 {process_id}] 查找登录/提交按钮出错: {e}")
                                            
                                            if submit_button:
                                                random_sleep(1.0, 2.0)
                                                
                                                # 使用JavaScript点击可能更可靠
                                                try:
                                                    driver.execute_script("arguments[0].click();", submit_button)
                                                    print(f"[进程 {process_id}] 已使用JavaScript点击登录/提交按钮")
                                                except Exception as js_err:
                                                    print(f"[进程 {process_id}] JavaScript点击登录按钮失败: {js_err}")
                                                    # 如果JavaScript点击失败，尝试常规点击
                                                    action = ActionChains(driver)
                                                    action.move_to_element(submit_button).click().perform()
                                                    print(f"[进程 {process_id}] 已使用ActionChains点击登录/提交按钮")
                                                
                                                print(f"[进程 {process_id}] 登录流程完成")
                                            else:
                                                print(f"[进程 {process_id}] 未找到登录/提交按钮")
                                        except Exception as input_err:
                                            print(f"[进程 {process_id}] 输入验证码时出错: {input_err}")
                                    else:
                                        print(f"[进程 {process_id}] 未找到验证码输入框")
                                else:
                                    print(f"[进程 {process_id}] 未能获取验证码，流程无法继续")
                        else:
                            print(f"[进程 {process_id}] 获取验证码按钮被禁用，可能在倒计时")
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