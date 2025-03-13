from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading

# 全局变量存储浏览器驱动实例，防止被垃圾回收
browser_drivers = []

def auto_fill_phone(phone_number):
    """
    自动打开SiliconFlow登录页面并填写手机号
    
    参数:
        phone_number (str): 要填写的手机号码
    """
    global browser_drivers
    
    print(f"开始为手机号 {phone_number} 自动填写表单...")
    
    # 初始化Chrome浏览器
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)  # 重要：使浏览器在脚本执行完后保持打开
    # options.add_argument('--headless')  # 无头模式，取消注释可不显示浏览器窗口
    
    # 初始化WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # 将驱动实例添加到全局列表中，防止被垃圾回收
    browser_drivers.append(driver)
    
    try:
        # 打开登录页面
        url = "https://account.siliconflow.cn/zh/login?redirect=https%3A%2F%2Fcloud.siliconflow.cn%2F%3F"
        driver.get(url)
        print(f"已为手机号 {phone_number} 打开登录页面")
        
        # 等待页面加载
        time.sleep(2)
        
        # 找到手机号输入框并填写
        # 这里需要根据实际网页元素定位手机号输入框
        # 可能的选择器包括：id、name、class name、XPath等
        # 下面是一些常见的选择方法，可能需要调整
        try:
            # 尝试通过placeholder找到输入框
            phone_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入手机号' or contains(@placeholder, '手机号')]"))
            )
            phone_input.clear()
            phone_input.send_keys(phone_number)
            print(f"已成功填写手机号: {phone_number}")
            
            # 等待一段时间以便查看结果
            time.sleep(5)
            
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
        # 等待一小段时间，避免同时启动多个浏览器导致资源竞争
        time.sleep(1)
    
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