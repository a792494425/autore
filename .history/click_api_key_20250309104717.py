import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import random

def random_sleep(min_seconds=0.5, max_seconds=2.0):
    """随机睡眠一段时间，模拟人类行为"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def click_api_key_buttons(driver_port):
    """
    点击API密钥菜单和新建API密钥按钮
    
    参数:
        driver_port (int): Chrome远程调试端口
    """
    try:
        # 连接到已打开的Chrome浏览器
        print(f"尝试连接到Chrome浏览器（端口: {driver_port}）...")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{driver_port}")
        
        # 创建Service对象
        service = Service()
        
        # 创建WebDriver对象
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"已连接到Chrome浏览器")
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(3)
        
        # 尝试点击API密钥菜单
        print("尝试点击API密钥菜单...")
        try:
            # 使用多种选择器查找API密钥菜单
            api_key_selectors = [
                "//li[contains(@class, 'ant-menu-item') and contains(@data-menu-id, 'account/ak')]",
                "//li[contains(@class, 'ant-menu-item')]//span[text()='API 密钥']/..",
                "//li[contains(@class, 'ant-menu-item')]//svg/following-sibling::span[contains(text(), 'API')]/parent::li",
                "//li[contains(@class, 'ant-menu-item')]//svg[contains(@class, 'ant-menu-item-icon')]/parent::li"
            ]
            
            api_menu = None
            for selector in api_key_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        api_menu = elements[0]
                        print(f"找到API密钥菜单: {selector}")
                        break
                except:
                    continue
            
            if api_menu:
                # 点击菜单
                driver.execute_script("arguments[0].scrollIntoView(true);", api_menu)
                driver.execute_script("arguments[0].click();", api_menu)
                print("已点击API密钥菜单")
            else:
                # 如果找不到菜单，使用JavaScript查找并点击
                js_click_menu = """
                (function() {
                    var items = document.querySelectorAll('li.ant-menu-item');
                    for (var i = 0; i < items.length; i++) {
                        if (items[i].textContent.indexOf('API') >= 0 && items[i].textContent.indexOf('密钥') >= 0) {
                            items[i].click();
                            return true;
                        }
                    }
                    return false;
                })();
                """
                menu_clicked = driver.execute_script(js_click_menu)
                if menu_clicked:
                    print("已通过JavaScript点击API密钥菜单")
                else:
                    # 尝试通过URL直接导航
                    current_url = driver.current_url
                    api_key_url = current_url.split('?')[0].rstrip('/') + "/account/ak"
                    driver.get(api_key_url)
                    print(f"已直接导航到API密钥页面: {api_key_url}")
            
            # 等待API密钥页面加载
            print("等待API密钥页面加载...")
            time.sleep(3)
            
            # 尝试点击新建API密钥按钮
            print("尝试点击'新建 API 密钥'按钮...")
            try:
                # 使用多种选择器查找新建API密钥按钮
                button_selectors = [
                    "//button[contains(@class, 'ant-btn') and contains(@class, 'ant-btn-primary')]/span[text()='新建 API 密钥']/parent::button",
                    "//button[contains(@class, 'ant-btn-primary') and contains(., '新建 API 密钥')]",
                    "//button[contains(@class, 'ant-btn-primary')]/span[contains(text(), '新建')]/parent::button",
                    "//button[contains(@class, 'ant-btn-primary')]"
                ]
                
                new_key_button = None
                for selector in button_selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        if elements:
                            new_key_button = elements[0]
                            print(f"找到'新建 API 密钥'按钮: {selector}")
                            break
                    except:
                        continue
                
                if new_key_button:
                    # 点击按钮
                    driver.execute_script("arguments[0].scrollIntoView(true);", new_key_button)
                    driver.execute_script("arguments[0].click();", new_key_button)
                    print("已点击'新建 API 密钥'按钮")
                else:
                    # 如果找不到按钮，使用JavaScript查找并点击
                    js_click_button = """
                    (function() {
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            if (buttons[i].textContent.indexOf('新建') >= 0 && buttons[i].textContent.indexOf('API') >= 0) {
                                buttons[i].click();
                                return true;
                            }
                        }
                        return false;
                    })();
                    """
                    button_clicked = driver.execute_script(js_click_button)
                    if button_clicked:
                        print("已通过JavaScript点击'新建 API 密钥'按钮")
                    else:
                        print("无法找到'新建 API 密钥'按钮")
                
                # 等待模态框出现
                print("等待模态框出现...")
                time.sleep(2)
                
                # 填写描述
                try:
                    description_input = driver.find_element(By.ID, "description")
                    description_text = f"Auto API Key - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    description_input.clear()
                    description_input.send_keys(description_text)
                    print(f"已输入描述: {description_text}")
                except:
                    # 如果找不到输入框，使用JavaScript查找并设置值
                    description_text = f"Auto API Key - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    js_set_desc = f"""
                    (function() {{
                        var input = document.getElementById('description');
                        if (!input) {{
                            input = document.querySelector('input[placeholder*="描述"]');
                        }}
                        if (input) {{
                            input.value = "{description_text}";
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            return true;
                        }}
                        return false;
                    }})();
                    """
                    if driver.execute_script(js_set_desc):
                        print(f"已通过JavaScript输入描述: {description_text}")
                    else:
                        print("无法找到描述输入框")
                
                # 点击确认按钮
                print("尝试点击确认按钮...")
                try:
                    # 使用多种选择器查找确认按钮
                    confirm_selectors = [
                        "//div[contains(@class, 'ant-modal-footer')]/button[contains(@class, 'ant-btn-primary')]/span[text()='新建密钥']/parent::button",
                        "//div[contains(@class, 'ant-modal-footer')]/button[contains(@class, 'ant-btn-primary')]",
                        "//div[contains(@class, 'ant-modal-footer')]//button[last()]"
                    ]
                    
                    confirm_button = None
                    for selector in confirm_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            if elements:
                                confirm_button = elements[0]
                                print(f"找到确认按钮: {selector}")
                                break
                        except:
                            continue
                    
                    if confirm_button:
                        # 点击按钮
                        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
                        driver.execute_script("arguments[0].click();", confirm_button)
                        print("已点击确认按钮")
                    else:
                        # 如果找不到按钮，使用JavaScript查找并点击
                        js_click_confirm = """
                        (function() {
                            var modal = document.querySelector('.ant-modal-content');
                            if (modal) {
                                var footer = modal.querySelector('.ant-modal-footer');
                                if (footer) {
                                    var buttons = footer.querySelectorAll('button');
                                    for (var i = 0; i < buttons.length; i++) {
                                        if (buttons[i].textContent.indexOf('新建密钥') >= 0 || 
                                            (buttons[i].classList.contains('ant-btn-primary'))) {
                                            buttons[i].click();
                                            return true;
                                        }
                                    }
                                    // 点击最后一个按钮
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
                            print("已通过JavaScript点击确认按钮")
                        else:
                            print("无法找到确认按钮")
                except Exception as e:
                    print(f"点击确认按钮时出错: {e}")
            except Exception as e:
                print(f"点击'新建 API 密钥'按钮时出错: {e}")
        except Exception as e:
            print(f"点击API密钥菜单时出错: {e}")
        
        print("API密钥创建操作完成")
    except Exception as e:
        print(f"操作出错: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        click_api_key_buttons(port)
    else:
        print("请提供Chrome远程调试端口号")
        print("用法: python click_api_key.py <端口号>")
        print("例如: python click_api_key.py 9222") 