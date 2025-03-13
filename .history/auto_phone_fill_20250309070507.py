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

# 全局变量存储浏览器驱动实例，防止被垃圾回收
browser_drivers = []

def random_sleep(min_seconds=0.5, max_seconds=2.0):
    """随机睡眠一段时间，模拟人类行为"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def human_like_typing(element, text):
    """模拟人类输入，有随机间隔"""
    for char in text:
        element.send_keys(char)
        # 随机短暂停顿，模拟人类打字速度
        time.sleep(random.uniform(0.05, 0.25))

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
        random_sleep(1.0, 3.0)
        
        # 模拟人类行为 - 滚动页面
        driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)});")
        random_sleep(0.5, 1.5)
        driver.execute_script(f"window.scrollBy(0, {random.randint(-100, -50)});")
        random_sleep(0.3, 0.8)
        
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
            
            # 鼠标移动到输入框
            action = ActionChains(driver)
            action.move_to_element(phone_input).perform()
            random_sleep(0.3, 0.7)
            
            # 点击输入框
            action.click().perform()
            random_sleep(0.2, 0.6)
            
            # 清空输入框
            phone_input.clear()
            random_sleep(0.2, 0.4)
            
            # 模拟人类输入
            human_like_typing(phone_input, phone_number)
            
            print(f"已成功填写手机号: {phone_number}")
            
            # 随机延迟，模拟人类行为
            random_sleep(0.8, 1.5)
            
            # 可能的后续操作，如按下Tab键或点击获取验证码
            if random.choice([True, False]):
                action.send_keys(Keys.TAB).perform()
            else:
                # 尝试查找并点击验证码按钮，但不强制
                try:
                    code_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '验证码') or contains(text(), '获取')]")
                    if code_buttons:
                        # 鼠标移动到按钮
                        action.move_to_element(code_buttons[0]).perform()
                        random_sleep(0.3, 0.8)
                        # 不实际点击，让用户自己点击
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
        random_sleep(2.0, 5.0)
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("所有浏览器实例已启动并填写完毕")

def get_user_input_phones(browser_count):
    """
    获取用户输入的手机号
    
    参数:
        browser_count (int): 需要开启的浏览器数量
    
    返回:
        list: 用户输入的手机号列表
    """
    phone_numbers = []
    print(f"\n请输入{browser_count}个手机号，每个手机号输入完成后按回车确认:")
    
    for i in range(browser_count):
        while True:
            phone = input(f"请输入第 {i+1} 个手机号: ")
            
            # 简单验证手机号格式（11位数字）
            if phone.isdigit() and len(phone) == 11:
                phone_numbers.append(phone)
                break
            else:
                print("手机号格式不正确，请输入11位数字手机号!")
    
    print("\n您输入的手机号如下:")
    for i, phone in enumerate(phone_numbers):
        print(f"{i+1}. {phone}")
    
    # 移除确认步骤，直接返回手机号列表
    return phone_numbers

if __name__ == "__main__":
    # 获取用户输入的浏览器数量
    while True:
        try:
            browser_count = int(input("请输入需要开启的浏览器数量(1-10): "))
            if 1 <= browser_count <= 10:
                break
            else:
                print("请输入1到10之间的数字!")
        except ValueError:
            print("请输入有效的数字!")
    
    # 获取用户输入的手机号
    phone_numbers = get_user_input_phones(browser_count)
    
    # 直接运行，不再进行确认
    print("\n正在启动浏览器并填写手机号...")
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