from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def auto_fill_phone(phone_number):
    """
    自动打开SiliconFlow登录页面并填写手机号
    
    参数:
        phone_number (str): 要填写的手机号码
    """
    print(f"开始为手机号 {phone_number} 自动填写表单...")
    
    # 初始化Chrome浏览器
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 无头模式，取消注释可不显示浏览器窗口
    
    # 初始化WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 打开登录页面
        url = "https://account.siliconflow.cn/zh/login?redirect=https%3A%2F%2Fcloud.siliconflow.cn%2F%3F"
        driver.get(url)
        print("已打开登录页面")
        
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
            
    finally:
        # 关闭浏览器
        # 注释掉下一行可以保持浏览器打开以便查看结果
        # driver.quit()
        print("脚本执行完毕")

if __name__ == "__main__":
    # 在这里输入您想要填写的手机号
    phone_number = "13800138000"  # 替换成您想要填写的手机号
    auto_fill_phone(phone_number) 