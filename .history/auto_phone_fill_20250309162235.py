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
import shutil
import signal
import atexit
from multiprocessing import Manager
import base64
import io
import subprocess
import tempfile

# 条件导入
has_pil = False
has_pytesseract = False

try:
    from PIL import Image
    has_pil = True
except ImportError:
    print("警告: 未找到PIL(Pillow)模块，截图OCR功能将不可用")
    print("请运行 'pip install pillow' 以启用完整的OCR功能")

try:
    import pytesseract
    has_pytesseract = True
except ImportError:
    if has_pil:  # 只有在PIL可用时才显示pytesseract警告
        print("警告: 未找到pytesseract模块，OCR功能将受限")
        print("请运行 'pip install pytesseract' 并安装Tesseract OCR引擎以启用完整OCR功能")

try:
    import pyperclip  # 尝试导入pyperclip库用于获取剪贴板内容
except ImportError:
    pyperclip = None  # 如果不可用，设置为None

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

def extract_text_from_image(image_bytes):
    """
    使用OCR从图像中提取文本
    """
    # 检查是否有PIL库
    if not has_pil:
        print("未安装PIL库，无法处理图像")
        return ""
        
    if has_pytesseract:
        try:
            # 使用pytesseract进行OCR
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as ocr_err:
            print(f"使用pytesseract OCR提取文本失败: {ocr_err}")
    
    # 尝试使用命令行工具作为备用
    try:
        # 保存图像到临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(image_bytes)
        
        # 检查操作系统类型，选择合适的OCR命令
        if os.name == 'nt':  # Windows
            # 尝试使用Windows OCR或其他可用工具
            # 这里仅作示例，实际实现需要根据系统上安装的工具进行调整
            try:
                result = subprocess.run(['powershell', '-Command', 
                                        f"Add-Type -AssemblyName System.Drawing; " +
                                        f"Add-Type -AssemblyName System.Windows.Forms; " +
                                        f"[System.Windows.Forms.Clipboard]::GetText()"],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass
        else:  # Linux/Mac
            # 尝试使用tesseract命令行
            try:
                result = subprocess.run(['tesseract', temp_path, 'stdout'], 
                                       capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
        
        # 清理临时文件
        try:
            os.unlink(temp_path)
        except:
            pass
    except Exception as cmd_err:
        print(f"使用命令行OCR提取文本失败: {cmd_err}")
    
    return ""

def find_api_key_in_text(text):
    """
    从文本中提取API密钥
    """
    # 查找SK格式的API密钥
    sk_pattern = r'sk-[a-zA-Z0-9]{48,}'
    matches = re.findall(sk_pattern, text)
    if matches:
        return max(matches, key=len)  # 返回最长的匹配项
    return None

def extract_api_key(driver, process_id, phone_number):
    """提取API密钥信息的辅助函数"""
    try:
        print(f"[进程 {process_id}] 开始提取API密钥信息...")
        
        # 初始化key_text变量，确保不会出现未定义错误
        key_text = None
        
        # 等待一段时间，确保密钥列表已更新
        random_sleep(2.0, 3.0)
        
        # 查找表格中的密钥信息 - 精确定位带星号的密钥
        key_selectors = [
            "//td[contains(@class, 'ant-table-cell')]//span[contains(text(), 'sk-')]",  # 直接匹配用户提供的HTML结构
            "//td[contains(text(), 'sk-')]",  # 包含sk-前缀的表格单元格
            "//div[contains(text(), 'sk-')]", # 包含sk-前缀的div元素
            "//span[contains(text(), 'sk-')]", # 包含sk-前缀的span元素
            "//table//tr[1]//td[1]" # 第一行第一列，通常是密钥
        ]
        
        key_element = None
        for selector in key_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                # 查找包含星号的元素，这通常表示是隐藏的密钥
                for element in elements:
                    if "*" in element.text:
                        key_element = element
                        print(f"[进程 {process_id}] 找到带星号的密钥元素: {element.text}")
                        break
                
                # 如果没找到带星号的，使用第一个元素
                if not key_element and elements:
                    key_element = elements[0]
                    print(f"[进程 {process_id}] 找到密钥元素: {elements[0].text}")
                
                if key_element:
                    break
        
        if not key_element:
            print(f"[进程 {process_id}] 未找到密钥元素")
            return None
        
        # 清空剪贴板
        if pyperclip:
            try:
                pyperclip.copy('')
            except Exception as clip_err:
                print(f"[进程 {process_id}] 清空剪贴板失败: {clip_err}")
        
        # 保存初始密钥文本，以防提取失败时使用
        initial_key_text = key_element.text.strip()
        
        # 尝试点击密钥元素以显示完整密钥和复制
        try:
            # 确保元素可见
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", key_element)
            random_sleep(0.5, 1.0)
            
            # 尝试直接点击
            driver.execute_script("arguments[0].click();", key_element)
            print(f"[进程 {process_id}] 已点击密钥元素")
            
            # 等待弹窗出现
            random_sleep(1.0, 2.0)
            
            # 处理可能出现的JavaScript警告框
            try:
                # 检查是否有alert并接受它
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"[进程 {process_id}] 检测到警告框: {alert_text}")
                
                # 如果是复制到剪贴板的警告框，可能已经有完整密钥
                if "Copy to clipboard" in alert_text or "复制到剪贴板" in alert_text:
                    # 警告框出现时，直接尝试从页面中提取密钥
                    extracted_key = extract_api_key_from_page(driver, process_id)
                    if extracted_key:
                        key_text = extracted_key
                        print(f"[进程 {process_id}] 警告框显示时成功提取到API密钥: {key_text[:5]}...{key_text[-5:]}")
                        
                        # 立即保存到文件
                        try:
                            with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                                f.write(f"{key_text}\n")
                            print(f"[进程 {process_id}] 已将API密钥保存到文件: all_api_keys.txt")
                        except Exception as save_err:
                            print(f"[进程 {process_id}] 保存API密钥失败: {save_err}")
                    
                    # 检查是否有PIL库支持
                    if has_pil:
                        # 截取整个页面的截图
                        try:
                            screenshot = driver.get_screenshot_as_base64()
                            screenshot_bytes = base64.b64decode(screenshot)
                            print(f"[进程 {process_id}] 已获取屏幕截图，准备OCR提取密钥")
                            
                            # 在警告框显示时使用OCR识别屏幕上的内容
                            screenshot_text = extract_text_from_image(screenshot_bytes)
                            
                            # 从OCR文本中查找API密钥
                            ocr_key = find_api_key_in_text(screenshot_text)
                            if ocr_key:
                                key_text = ocr_key
                                print(f"[进程 {process_id}] 通过OCR从截图中找到API密钥: {key_text[:5]}...{key_text[-5:]}")
                                
                                # 立即保存找到的密钥
                                try:
                                    with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                                        f.write(f"{key_text}\n")
                                    print(f"[进程 {process_id}] 已将通过OCR获取的API密钥保存到文件: all_api_keys.txt")
                                except Exception as save_err:
                                    print(f"[进程 {process_id}] 保存OCR获取的API密钥失败: {save_err}")
                            else:
                                print(f"[进程 {process_id}] OCR未能从截图中找到API密钥")
                        except Exception as ss_err:
                            print(f"[进程 {process_id}] 获取屏幕截图失败: {ss_err}")
                    else:
                        print(f"[进程 {process_id}] PIL库未安装，无法使用OCR功能")
                    
                    # 在警告框出现时，直接接受警告框，而不是用Ctrl+C
                    try:
                        # 直接接受警告框
                        alert.accept()
                        print(f"[进程 {process_id}] 已接受警告框")
                    except Exception as accept_err:
                        print(f"[进程 {process_id}] 接受警告框失败: {accept_err}")
                else:
                    # 如果不是复制相关的警告框，直接接受
                    alert.accept()
                    print(f"[进程 {process_id}] 已接受警告框")
                
                # 给系统一些时间更新剪贴板
                random_sleep(1.0, 1.5)
                
                # 警告框处理后立即检查剪贴板内容
                if pyperclip:
                    try:
                        clipboard_content = pyperclip.paste()
                        if clipboard_content and clipboard_content.startswith("sk-"):
                            key_text = clipboard_content
                            print(f"[进程 {process_id}] 警告框处理后从剪贴板获取到完整密钥!")
                            
                            # 立即将获取到的完整密钥保存到文件中
                            try:
                                with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                                    f.write(f"{key_text}\n")
                                print(f"[进程 {process_id}] 已将从警告框获取的API密钥保存到文件: all_api_keys.txt")
                            except Exception as save_err:
                                print(f"[进程 {process_id}] 保存从警告框获取的API密钥失败: {save_err}")
                    except Exception as clipboard_err:
                        print(f"[进程 {process_id}] 警告框处理后无法获取剪贴板内容: {clipboard_err}")
            except Exception as no_alert:
                # 没有alert，继续正常流程
                pass
            
            # 首先尝试从弹窗中获取完整密钥
            try:
                # 优先检查弹窗内容
                popup_key = driver.execute_script("""
                // 尝试获取弹窗中显示的完整密钥
                (function() {
                    // 检查各种可能的弹窗元素
                    var popups = [
                        document.querySelector('.ant-modal-content'),
                        document.querySelector('.ant-drawer-content'),
                        document.querySelector('.modal-content'),
                        document.querySelector('[role="dialog"]'),
                        document.querySelector('.popup'),
                        document.querySelector('.dialog')
                    ];
                    
                    for (var i = 0; i < popups.length; i++) {
                        var popup = popups[i];
                        if (!popup) continue;
                        
                        // 尝试直接获取弹窗中的文本内容
                        var popupText = popup.textContent || '';
                        var match = popupText.match(/sk-[a-zA-Z0-9]{48,}/);
                        if (match) return match[0];
                        
                        // 查找弹窗中可能包含密钥的元素
                        var keyElements = popup.querySelectorAll('div, span, p, input, textarea');
                        for (var j = 0; j < keyElements.length; j++) {
                            var el = keyElements[j];
                            var elText = el.textContent || el.value || '';
                            if (elText.includes('sk-') && !elText.includes('*')) {
                                var keyMatch = elText.match(/sk-[a-zA-Z0-9]{48,}/);
                                if (keyMatch) return keyMatch[0];
                            }
                        }
                    }
                    
                    return null;
                })();
                """)
                
                if popup_key and popup_key.startswith("sk-") and len(popup_key) >= 48:
                    print(f"[进程 {process_id}] 从弹窗中找到完整密钥!")
                    key_text = popup_key
                    
                    # 立即将获取到的完整密钥保存到文件中
                    try:
                        with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                            f.write(f"{key_text}\n")
                        print(f"[进程 {process_id}] 已将从弹窗中获取的API密钥保存到文件: all_api_keys.txt")
                    except Exception as save_err:
                        print(f"[进程 {process_id}] 保存从弹窗中获取的API密钥失败: {save_err}")
                    
                    # 尝试点击弹窗中的复制按钮
                    try:
                        driver.execute_script("""
                        // 尝试点击弹窗中的复制按钮
                        (function() {
                            var popups = document.querySelectorAll('.ant-modal-content, .ant-drawer-content, .modal-content, [role="dialog"], .popup, .dialog');
                            for (var i = 0; i < popups.length; i++) {
                                var popup = popups[i];
                                if (!popup) continue;
                                
                                // 查找各种可能的复制按钮
                                var copyButtons = popup.querySelectorAll('button, span, div');
                                for (var j = 0; j < copyButtons.length; j++) {
                                    var btn = copyButtons[j];
                                    if (btn.textContent.includes('复制') || 
                                        btn.textContent.includes('Copy') || 
                                        btn.className.includes('copy')) {
                                        btn.click();
                                        return true;
                                    }
                                }
                            }
                            return false;
                        })();
                        """)
                        print(f"[进程 {process_id}] 尝试点击弹窗中的复制按钮")
                        random_sleep(0.5, 1.0)
                        
                        # 再次检查是否有alert并接受它
                        try:
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            print(f"[进程 {process_id}] 检测到复制后的警告框: {alert_text}")
                            alert.accept()
                            print(f"[进程 {process_id}] 已接受复制后的警告框")
                            random_sleep(0.5, 1.0)
                        except:
                            pass
                    except Exception as popup_copy_err:
                        print(f"[进程 {process_id}] 点击弹窗复制按钮失败: {popup_copy_err}")
                else:
                    # 如果弹窗中没有找到完整密钥，检查是否有任何复制按钮并点击它
                    copy_button_selectors = [
                        "//button[contains(@class, 'copy')]",
                        "//button[.//span[contains(text(), '复制')]]",
                        "//span[contains(text(), '复制')]/parent::button",
                        "//svg[contains(@class, 'copy-icon')]/parent::button"
                    ]
                    
                    for copy_selector in copy_button_selectors:
                        try:
                            copy_buttons = driver.find_elements(By.XPATH, copy_selector)
                            if copy_buttons:
                                driver.execute_script("arguments[0].click();", copy_buttons[0])
                                print(f"[进程 {process_id}] 已点击复制按钮")
                                random_sleep(0.5, 1.0)
                                
                                # 检查是否有alert并接受它
                                try:
                                    alert = driver.switch_to.alert
                                    alert_text = alert.text
                                    print(f"[进程 {process_id}] 检测到复制后的警告框: {alert_text}")
                                    alert.accept()
                                    print(f"[进程 {process_id}] 已接受复制后的警告框")
                                    random_sleep(0.5, 1.0)
                                except:
                                    pass
                                
                                break
                        except Exception as copy_btn_err:
                            print(f"[进程 {process_id}] 点击复制按钮时出错: {copy_btn_err}")
                            continue
            except Exception as popup_err:
                print(f"[进程 {process_id}] 尝试从弹窗获取密钥失败: {popup_err}")
                
                # 使用原来的复制按钮点击逻辑作为备用
                try:
                    copy_button_selectors = [
                        "//button[contains(@class, 'copy')]",
                        "//button[.//span[contains(text(), '复制')]]",
                        "//span[contains(text(), '复制')]/parent::button",
                        "//svg[contains(@class, 'copy-icon')]/parent::button"
                    ]
                    
                    for copy_selector in copy_button_selectors:
                        copy_buttons = driver.find_elements(By.XPATH, copy_selector)
                        if copy_buttons:
                            driver.execute_script("arguments[0].click();", copy_buttons[0])
                            print(f"[进程 {process_id}] 已点击复制按钮")
                            random_sleep(0.5, 1.0)
                            
                            # 检查是否有alert并接受它
                            try:
                                alert = driver.switch_to.alert
                                alert_text = alert.text
                                print(f"[进程 {process_id}] 检测到复制后的警告框: {alert_text}")
                                alert.accept()
                                print(f"[进程 {process_id}] 已接受复制后的警告框")
                                random_sleep(0.5, 1.0)
                            except:
                                pass
                            
                            break
                except Exception as backup_copy_err:
                    print(f"[进程 {process_id}] 备用复制按钮点击失败: {backup_copy_err}")
        except Exception as click_err:
            print(f"[进程 {process_id}] 点击密钥元素失败: {click_err}")
        
        # 获取密钥文本（如果弹窗中没有找到）
        if not (key_text and key_text.startswith("sk-") and len(key_text) >= 48 and "*" not in key_text):
            key_text = initial_key_text  # 使用初始保存的文本
            
            # 尝试从剪贴板获取完整密钥
            if pyperclip:
                try:
                    clipboard_content = pyperclip.paste()
                    if clipboard_content and clipboard_content.startswith("sk-"):
                        key_text = clipboard_content
                        print(f"[进程 {process_id}] 已从剪贴板获取完整密钥")
                        
                        # 立即将获取到的完整密钥保存到文件中
                        try:
                            with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                                f.write(f"{key_text}\n")
                            print(f"[进程 {process_id}] 已将从剪贴板获取的API密钥保存到文件: all_api_keys.txt")
                        except Exception as save_err:
                            print(f"[进程 {process_id}] 保存从剪贴板获取的API密钥失败: {save_err}")
                except Exception as clipboard_err:
                    print(f"[进程 {process_id}] 无法从剪贴板获取内容: {clipboard_err}")
            
            # 如果密钥中包含*号且无法从剪贴板获取，尝试其他方法
            if "*" in key_text:
                try:
                    # 尝试从页面源码中查找完整的密钥
                    page_source = driver.page_source
                    # 使用正则表达式查找sk-开头的长字符串
                    sk_matches = re.findall(r'sk-[a-zA-Z0-9]{48,}', page_source)
                    if sk_matches:
                        # 取最长的匹配项作为完整密钥
                        key_text = max(sk_matches, key=len)
                        print(f"[进程 {process_id}] 从页面源码中找到密钥")
                        
                        # 立即将获取到的完整密钥保存到文件中
                        try:
                            with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                                f.write(f"{key_text}\n")
                            print(f"[进程 {process_id}] 已将从页面源码中获取的API密钥保存到文件: all_api_keys.txt")
                        except Exception as save_err:
                            print(f"[进程 {process_id}] 保存从页面源码中获取的API密钥失败: {save_err}")
                except Exception as regex_err:
                    print(f"[进程 {process_id}] 正则查找密钥失败: {regex_err}")
                
                # 尝试通过JavaScript查找输入框中的完整密钥
                if "*" in key_text:  # 如果还是有星号
                    try:
                        complete_key = driver.execute_script("""
                        return document.querySelector('input[type="text"][value*="sk-"]') ? 
                               document.querySelector('input[type="text"][value*="sk-"]').value : null;
                        """)
                        
                        if complete_key:
                            key_text = complete_key
                            print(f"[进程 {process_id}] 通过JavaScript找到完整密钥")
                            
                            # 立即将获取到的完整密钥保存到文件中
                            try:
                                with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                                    f.write(f"{key_text}\n")
                                print(f"[进程 {process_id}] 已将通过JavaScript获取的API密钥保存到文件: all_api_keys.txt")
                            except Exception as save_err:
                                print(f"[进程 {process_id}] 保存通过JavaScript获取的API密钥失败: {save_err}")
                    except Exception as js_err:
                        print(f"[进程 {process_id}] JavaScript查找密钥失败: {js_err}")
        
        # 确保key_text不为None
        if key_text is None:
            key_text = "未能提取到完整密钥"
            print(f"[进程 {process_id}] 警告: 未能提取到任何密钥文本")
        
        # 记录密钥信息
        print(f"[进程 {process_id}] 提取到API密钥: {key_text[:10]}...{key_text[-5:] if len(key_text) > 15 else key_text}")
        description_text = f"Auto API Key - {phone_number}"
        
        # 查找描述信息
        try:
            description_elements = driver.find_elements(By.XPATH, f"//td[contains(text(), '{phone_number}')]")
            if description_elements:
                description_text = description_elements[0].text.strip()
        except Exception as desc_err:
            print(f"[进程 {process_id}] 获取描述信息失败: {desc_err}")
        
        # 创建密钥信息字典
        key_info = {
            "key": key_text,
            "description": description_text,
            "phone": phone_number,
            "creation_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 立即将API密钥写入文本文件
        try:
            # 检查密钥是否包含星号，只有完整密钥才保存
            if "*" not in key_text and key_text.startswith("sk-") and len(key_text) >= 48:
                # 将密钥追加到一个公共文件中
                with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                    f.write(f"{key_text}\n")
                
                print(f"[进程 {process_id}] 已将完整API密钥追加到文件: all_api_keys.txt")
            else:
                print(f"[进程 {process_id}] 警告: 未能获取完整密钥，跳过保存到文件")
                
                # 额外尝试从页面获取完整密钥的方法
                try:
                    # 尝试使用更多JavaScript方法获取完整密钥
                    js_extract_code = """
                    // 尝试多种方法找到完整的API密钥
                    (function() {
                        // 方法1: 查找所有包含sk-的元素的data属性
                        var allElements = document.querySelectorAll('*');
                        for (var i = 0; i < allElements.length; i++) {
                            var el = allElements[i];
                            for (var j = 0; j < el.attributes.length; j++) {
                                var attr = el.attributes[j];
                                if (attr.value && attr.value.includes('sk-') && !attr.value.includes('*')) {
                                    var match = attr.value.match(/sk-[a-zA-Z0-9]{48,}/);
                                    if (match) return match[0];
                                }
                            }
                        }
                        
                        // 方法2: 检查所有输入框
                        var inputs = document.querySelectorAll('input');
                        for (var i = 0; i < inputs.length; i++) {
                            if (inputs[i].value && inputs[i].value.includes('sk-') && !inputs[i].value.includes('*')) {
                                return inputs[i].value;
                            }
                        }
                        
                        // 方法3: 检查所有的span和div内容
                        var textElements = document.querySelectorAll('span, div, td');
                        for (var i = 0; i < textElements.length; i++) {
                            if (textElements[i].textContent && 
                                textElements[i].textContent.includes('sk-') && 
                                !textElements[i].textContent.includes('*')) {
                                var match = textElements[i].textContent.match(/sk-[a-zA-Z0-9]{48,}/);
                                if (match) return match[0];
                            }
                        }
                        
                        return null;
                    })();
                    """
                    
                    additional_key = driver.execute_script(js_extract_code)
                    if additional_key and additional_key.startswith("sk-") and len(additional_key) >= 48 and "*" not in additional_key:
                        print(f"[进程 {process_id}] 通过额外JavaScript方法找到完整密钥")
                        with open("all_api_keys.txt", "a", encoding="utf-8") as f:
                            f.write(f"{additional_key}\n")
                        print(f"[进程 {process_id}] 已将完整API密钥追加到文件: all_api_keys.txt")
                        # 更新密钥信息
                        key_text = additional_key
                        key_info["key"] = additional_key
                except Exception as extra_js_err:
                    print(f"[进程 {process_id}] 额外JavaScript提取密钥失败: {extra_js_err}")
            
        except Exception as save_err:
            print(f"[进程 {process_id}] 保存API密钥到文件失败: {save_err}")
        
        # 返回密钥信息供程序其他部分使用
        return key_info
    
    except Exception as extract_err:
        print(f"[进程 {process_id}] 提取密钥信息失败: {extract_err}")
        return None

def auto_fill_phone(phone_number, process_id, sid="87264", invitation_code=None, extracted_keys=None):
    """
    自动填写手机号并点击获取验证码
    
    参数:
        phone_number (str): 要填写的手机号
        process_id (str): 进程ID，用于日志区分
        sid (str): 验证码API的项目ID，默认为87264
        invitation_code (str): 邀请码，如果不需要则为None
        extracted_keys (dict): 共享字典，用于存储提取的密钥
    """
    # 创建一个临时目录用于存储Chrome用户数据
    user_data_dir = f"chrome_user_data_{process_id}_{uuid.uuid4().hex[:8]}"
    os.makedirs(user_data_dir, exist_ok=True)
    
    # 为进程创建独立的chromedriver目录
    driver_temp_dir = f"chromedriver_tmp_{process_id}_{uuid.uuid4().hex[:8]}"
    os.makedirs(driver_temp_dir, exist_ok=True)
    
    # 保存目录以便后续清理
    if not hasattr(auto_fill_phone, 'user_data_dirs'):
        auto_fill_phone.user_data_dirs = []
    auto_fill_phone.user_data_dirs.append(user_data_dir)
    
    if not hasattr(auto_fill_phone, 'driver_temp_dirs'):
        auto_fill_phone.driver_temp_dirs = []
    auto_fill_phone.driver_temp_dirs.append(driver_temp_dir)
    
    driver = None
    try:
        print(f"[进程 {process_id}] 正在启动Chrome浏览器...")
        
        # 创建Chrome选项
        options = uc.ChromeOptions()
        options.add_argument(f'--user-data-dir={os.path.abspath(user_data_dir)}')
        options.add_argument('--disable-popup-blocking')  # 禁用弹出窗口阻止
        options.add_argument('--disable-extensions')  # 禁用扩展
        options.add_argument('--no-sandbox')  # 禁用沙盒模式
        options.add_argument('--disable-gpu')  # 禁用GPU加速
        options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
        
        # 避免检测
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 在网站上显示为正常的Chrome
        options.add_argument("--window-size=1920,1080")
        
        # 创建多个尝试，避免偶发的文件冲突
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # 使用自定义临时目录和配置来创建浏览器
                driver = uc.Chrome(
                    options=options,
                    driver_executable_path=None,  # 自动下载
                    browser_executable_path=None,  # 自动检测
                    use_subprocess=True,
                    user_data_dir=os.path.abspath(user_data_dir),
                    temp_dir=os.path.abspath(driver_temp_dir)
                )
                # 成功创建浏览器，跳出循环
                break
            except Exception as browser_err:
                if attempt < max_attempts - 1:
                    print(f"[进程 {process_id}] 启动浏览器尝试 {attempt+1}/{max_attempts} 失败: {browser_err}")
                    # 删除可能导致冲突的文件
                    try:
                        for file_path in [
                            os.path.join(os.path.expanduser("~"), "appdata", "roaming", "undetected_chromedriver", "undetected_chromedriver.exe"),
                            os.path.join(driver_temp_dir, "chromedriver.exe")
                        ]:
                            if os.path.exists(file_path):
                                try:
                                    os.remove(file_path)
                                    print(f"[进程 {process_id}] 已删除可能冲突的文件: {file_path}")
                                except:
                                    pass
                    except:
                        pass
                    # 随机延迟，避免多个进程同时尝试
                    time.sleep(random.uniform(1.0, 3.0) * (attempt + 1))
                else:
                    # 最后一次尝试失败，抛出异常
                    raise
        
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
            
            # 如果有邀请码，尝试填写邀请码
            if invitation_code:
                try:
                    # 尝试查找邀请码输入框
                    invitation_selectors = [
                        "//input[@id='shareCode']",
                        "//input[@placeholder='邀请码（选填）']",
                        "//span[contains(@class, 'ant-input-affix-wrapper')]//input[@maxlength='8']"
                    ]
                    
                    invitation_input = None
                    for selector in invitation_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            if elements:
                                invitation_input = elements[0]
                                print(f"[进程 {process_id}] 已找到邀请码输入框")
                                break
                        except Exception as e:
                            continue
                    
                    if invitation_input:
                        # 点击输入框
                        invitation_input.click()
                        # 清空输入框
                        invitation_input.clear()
                        # 输入邀请码
                        invitation_input.send_keys(invitation_code)
                        print(f"[进程 {process_id}] 已成功填写邀请码: {invitation_code}")
                    else:
                        print(f"[进程 {process_id}] 未找到邀请码输入框")
                except Exception as invitation_error:
                    print(f"[进程 {process_id}] 填写邀请码时出错: {invitation_error}")
            
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
                                            
                                            try:
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
                                                
                                                # 等待登录成功后的页面加载，减少等待时间
                                                print(f"[进程 {process_id}] 等待页面加载完成...")
                                                random_sleep(1.0, 1.5)  # 减少等待时间
                                                
                                                # 一次性完成所有三个步骤，使用更简洁的JavaScript实现
                                                try:
                                                    print(f"[进程 {process_id}] 开始执行API密钥创建流程...")
                                                    
                                                    # 使用单一JavaScript操作完成所有步骤，避免多次元素查找
                                                    description_text = f"Auto API Key - {phone_number}"
                                                    js_api_key_flow = f"""
                                                    (function() {{
                                                        // 获取当前页面URL，判断当前状态
                                                        var currentUrl = window.location.href;
                                                        var isAPIKeyPage = currentUrl.includes('account/ak');
                                                        var hasModal = document.querySelector('.ant-modal-content') !== null;
                                                        
                                                        // 根据不同状态执行不同步骤
                                                        if (hasModal) {{
                                                            console.log('模态框已显示，直接执行步骤3');
                                                            // 填写描述并点击提交
                                                            completeStep3("{description_text}");
                                                            return 3; // 返回执行的步骤
                                                        }} else if (isAPIKeyPage) {{
                                                            console.log('已在API密钥页面，执行步骤2-3');
                                                            // 点击新建按钮并填写描述
                                                            if (completeStep2()) {{
                                                                setTimeout(function() {{
                                                                    completeStep3("{description_text}");
                                                                }}, 800);
                                                            }}
                                                            return 2; // 返回执行的步骤
                                                        }} else {{
                                                            console.log('执行完整流程步骤1-2-3');
                                                            // 执行完整流程
                                                            if (completeStep1()) {{
                                                                setTimeout(function() {{
                                                                    if (completeStep2()) {{
                                                                        setTimeout(function() {{
                                                                            completeStep3("{description_text}");
                                                                        }}, 800);
                                                                    }}
                                                                }}, 800);
                                                            }}
                                                            return 1; // 返回执行的步骤
                                                        }}
                                                        
                                                        // 步骤1：点击API密钥菜单
                                                        function completeStep1() {{
                                                            // 直接查找API密钥菜单元素
                                                            var menuItems = document.querySelectorAll('li.ant-menu-item');
                                                            var apiKeyMenu = null;
                                                            
                                                            for (var i = 0; i < menuItems.length; i++) {{
                                                                if (menuItems[i].textContent.includes('API 密钥')) {{
                                                                    apiKeyMenu = menuItems[i];
                                                                    break;
                                                                }}
                                                            }}
                                                            
                                                            if (apiKeyMenu) {{
                                                                apiKeyMenu.click();
                                                                console.log('点击了API密钥菜单');
                                                                return true;
                                                            }} else {{
                                                                console.log('未找到API密钥菜单');
                                                                return false;
                                                            }}
                                                        }}
                                                        
                                                        // 步骤2：点击新建API密钥按钮
                                                        function completeStep2() {{
                                                            var buttons = document.querySelectorAll('button');
                                                            var createButton = null;
                                                            
                                                            for (var i = 0; i < buttons.length; i++) {{
                                                                if (buttons[i].textContent.includes('新建 API 密钥')) {{
                                                                    createButton = buttons[i];
                                                                    break;
                                                                }}
                                                            }}
                                                            
                                                            if (createButton) {{
                                                                createButton.click();
                                                                console.log('点击了新建API密钥按钮');
                                                                return true;
                                                            }} else {{
                                                                console.log('未找到新建API密钥按钮');
                                                                return false;
                                                            }}
                                                        }}
                                                        
                                                        // 步骤3：填写描述并提交
                                                        function completeStep3(description) {{
                                                            var descInput = document.getElementById('description');
                                                            if (descInput) {{
                                                                descInput.value = description;
                                                                
                                                                // 手动触发输入事件，确保React组件捕获更改
                                                                var event = new Event('input', {{ bubbles: true }});
                                                                descInput.dispatchEvent(event);
                                                                
                                                                // 查找并点击确认按钮
                                                                var footerButtons = document.querySelectorAll('.ant-modal-footer button');
                                                                var confirmButton = null;
                                                                
                                                                for (var i = 0; i < footerButtons.length; i++) {{
                                                                    if (footerButtons[i].classList.contains('ant-btn-primary')) {{
                                                                        confirmButton = footerButtons[i];
                                                                        break;
                                                                    }}
                                                                }}
                                                                
                                                                if (confirmButton) {{
                                                                    confirmButton.click();
                                                                    console.log('提交了表单');
                                                                    return true;
                                                                }} else {{
                                                                    console.log('未找到确认按钮');
                                                                    return false;
                                                                }}
                                                            }} else {{
                                                                console.log('未找到描述输入框');
                                                                return false;
                                                            }}
                                                        }}
                                                    }})();
                                                    """
                                                    
                                                    # 执行JavaScript
                                                    step_result = driver.execute_script(js_api_key_flow)
                                                    print(f"[进程 {process_id}] 已启动完整API密钥创建流程（步骤{step_result}）")
                                                    
                                                    # 等待JavaScript操作完成
                                                    random_sleep(2.0, 3.0)
                                                    print(f"[进程 {process_id}] 等待API密钥创建完成...")
                                                    
                                                    # 检查是否成功（可选，不中断流程）
                                                    try:
                                                        success_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-message-success')]")
                                                        if success_elements:
                                                            print(f"[进程 {process_id}] 检测到成功消息，API密钥创建成功")
                                                            
                                                            # 额外步骤：提取完整的密钥信息
                                                            key_info = extract_api_key(driver, process_id, phone_number)
                                                            
                                                            # 如果提供了共享字典且提取到密钥，则存储密钥
                                                            if extracted_keys is not None and key_info:
                                                                extracted_keys[process_id] = key_info
                                                    except Exception as check_err:
                                                        print(f"[进程 {process_id}] 检查成功状态时出错: {check_err}")
                                                    
                                                    print(f"[进程 {process_id}] API密钥创建流程执行完毕")
                                                except Exception as js_api_key_error:
                                                    print(f"[进程 {process_id}] 执行JavaScript API密钥创建流程出错: {js_api_key_error}")
                                                    # 简单的备用方法（如果JavaScript方法失败）
                                                    try:
                                                        print(f"[进程 {process_id}] 尝试使用备用Selenium方法...")
                                                        
                                                        # 步骤1: 使用快速精确的选择器点击API密钥菜单
                                                        try:
                                                            menu_item = driver.find_element(By.XPATH, "//li[contains(@class, 'ant-menu-item')]//span[text()='API 密钥']/parent::li")
                                                            driver.execute_script("arguments[0].click();", menu_item)
                                                            random_sleep(0.5, 1.0)
                                                        except Exception as menu_err:
                                                            print(f"[进程 {process_id}] 尝试点击API密钥菜单失败: {menu_err}")
                                                        
                                                        # 步骤2: 使用快速精确的选择器点击新建API密钥按钮
                                                        try:
                                                            create_button = driver.find_element(By.XPATH, "//button/span[text()='新建 API 密钥']/parent::button")
                                                            driver.execute_script("arguments[0].click();", create_button)
                                                            random_sleep(0.5, 1.0)
                                                        except Exception as button_err:
                                                            print(f"[进程 {process_id}] 尝试点击新建API密钥按钮失败: {button_err}")
                                                        
                                                        # 步骤3: 填写描述并点击确认
                                                        try:
                                                            # 查找描述输入框
                                                            desc_input = driver.find_element(By.ID, "description")
                                                            desc_input.clear()
                                                            desc_input.send_keys(f"Auto API Key - {phone_number}")
                                                            
                                                            # 点击确认按钮
                                                            confirm_button = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-primary')]")
                                                            driver.execute_script("arguments[0].click();", confirm_button)
                                                        except Exception as form_err:
                                                            print(f"[进程 {process_id}] 尝试填写表单并提交失败: {form_err}")
                                                    except Exception as backup_error:
                                                        print(f"[进程 {process_id}] 备用方法也失败: {backup_error}")
                                            except Exception as click_err:
                                                print(f"[进程 {process_id}] 点击登录按钮过程中出错: {click_err}")
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
                            except Exception as direct_click_error:
                                try:
                                    action = ActionChains(driver)
                                    action.move_to_element(code_button).click().perform()
                                    print(f"[进程 {process_id}] 已通过ActionChains点击获取验证码按钮")
                                except Exception as action_error:
                                    print(f"[进程 {process_id}] 所有点击方法都失败: {action_error}")
                                    return
                            
                            random_sleep(2.0, 3.0)
                            verification_code = get_verification_code(phone_number, process_id, sid)
                            
                            # 重复处理验证码的代码（与上面类似）
                            # 为简化缩进问题，可以考虑将此部分逻辑提取为单独的函数
                            if verification_code:
                                # 处理验证码输入和提交
                                try:
                                    # 查找验证码输入框
                                    code_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, '验证码')]")
                                    code_input.clear()
                                    code_input.send_keys(verification_code)
                                    print(f"[进程 {process_id}] 已输入验证码: {verification_code}")
                                    
                                    # 点击提交按钮
                                    submit_btn = driver.find_element(By.XPATH, "//button[contains(@type, 'submit')]")
                                    driver.execute_script("arguments[0].click();", submit_btn)
                                    print(f"[进程 {process_id}] 已点击提交按钮")
                                except Exception as fallback_err:
                                    print(f"[进程 {process_id}] 备用验证码处理失败: {fallback_err}")
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
                        except Exception as btn_err:
                            print(f"获取按钮信息出错: {btn_err}")
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

def open_multiple_browsers(phone_numbers, sid="87264", invitation_code=None, extracted_keys=None):
    """
    使用多进程打开多个浏览器实例并填写不同的手机号
    
    参数:
        phone_numbers (list): 要填写的手机号列表
        sid (str): 验证码API的项目ID，默认为87264
        invitation_code (str): 邀请码，如果不需要则为None
        extracted_keys (dict): 共享字典，用于存储提取的密钥
    """
    processes = []
    
    # 为每个手机号创建一个进程
    for i, phone in enumerate(phone_numbers):
        # 为每个进程分配一个ID
        process_id = str(i + 1)
        
        # 创建进程
        process = multiprocessing.Process(
            target=auto_fill_phone, 
            args=(phone, process_id, sid, invitation_code, extracted_keys)
        )
        
        processes.append(process)
    
    # 启动所有进程
    for i, process in enumerate(processes):
        print(f"正在启动第 {i+1}/{len(processes)} 个浏览器实例...")
        process.start()
        # 每个浏览器启动间隔随机延迟，但减少延迟时间以加快启动速度
        time.sleep(random.uniform(2.0, 4.0))
    
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

# 在脚本退出时清理所有临时目录
def cleanup_temp_directories(extracted_keys=None):
    """清理所有临时Chrome用户数据目录"""
    # 先保存提取到的密钥信息
    if extracted_keys:
        save_api_keys(extracted_keys)
    
    print("\n正在清理临时目录...")
    
    # 从auto_fill_phone函数获取保存的Chrome用户数据目录列表
    if hasattr(auto_fill_phone, 'user_data_dirs'):
        for directory in auto_fill_phone.user_data_dirs:
            try:
                if os.path.exists(directory):
                    print(f"删除目录: {directory}")
                    shutil.rmtree(directory, ignore_errors=True)
            except Exception as e:
                print(f"删除目录 {directory} 时出错: {e}")
    
    # 清理chromedriver临时目录
    if hasattr(auto_fill_phone, 'driver_temp_dirs'):
        for directory in auto_fill_phone.driver_temp_dirs:
            try:
                if os.path.exists(directory):
                    print(f"删除chromedriver临时目录: {directory}")
                    shutil.rmtree(directory, ignore_errors=True)
            except Exception as e:
                print(f"删除chromedriver临时目录 {directory} 时出错: {e}")
    
    # 额外搜索可能遗留的临时目录
    try:
        for item in os.listdir('.'):
            if os.path.isdir(item) and (item.startswith('chrome_user_data_') or item.startswith('chromedriver_tmp_')):
                try:
                    print(f"删除遗留目录: {item}")
                    shutil.rmtree(item, ignore_errors=True)
                except Exception as e:
                    print(f"删除遗留目录 {item} 时出错: {e}")
    except Exception as e:
        print(f"搜索遗留目录时出错: {e}")
    
    # 在程序完全退出时删除密钥文件
    try:
        key_files = ["extracted_api_keys.txt", "all_api_keys.txt"]
        for key_file in key_files:
            if os.path.exists(key_file):
                print(f"删除密钥文件: {key_file}")
                os.remove(key_file)
    except Exception as e:
        print(f"删除密钥文件时出错: {e}")
    
    print("清理完成")

# 保存提取到的API密钥
def save_api_keys(extracted_keys):
    """将提取到的API密钥保存到文本文件"""
    if not extracted_keys:
        print("没有提取到任何API密钥，跳过保存")
        return
    
    try:
        with open("extracted_api_keys.txt", "w", encoding="utf-8") as f:
            f.write("提取的API密钥信息：\n")
            f.write("=" * 80 + "\n\n")
            
            for process_id, key_info in extracted_keys.items():
                f.write(f"手机号: {key_info.get('phone', 'unknown')}\n")
                f.write(f"描述: {key_info.get('description', 'unknown')}\n")
                f.write(f"密钥: {key_info.get('key', 'unknown')}\n")
                f.write(f"创建时间: {key_info.get('creation_time', 'unknown')}\n")
                f.write("-" * 80 + "\n\n")
            
        print(f"\n已将 {len(extracted_keys)} 个API密钥信息保存到 extracted_api_keys.txt")
        print("注意：此文件将在程序退出时自动删除，请及时复制所需信息")
    except Exception as e:
        print(f"保存API密钥信息时出错: {e}")

def extract_api_key_from_page(driver, process_id):
    """
    尝试多种方法从页面中提取API密钥，不依赖OCR
    """
    key_text = None
    
    # 方法1: 使用JavaScript查找页面上所有可能包含密钥的元素
    try:
        js_result = driver.execute_script("""
        // 尝试查找页面上所有可能包含密钥的元素
        (function() {
            var results = [];
            
            // 方法1: 查找所有文本节点
            var allElements = document.querySelectorAll('*');
            for (var i = 0; i < allElements.length; i++) {
                var el = allElements[i];
                if (el.childNodes && el.childNodes.length > 0) {
                    for (var j = 0; j < el.childNodes.length; j++) {
                        var node = el.childNodes[j];
                        if (node.nodeType === 3) { // 文本节点
                            var text = node.nodeValue;
                            if (text && text.includes('sk-')) {
                                var match = text.match(/sk-[a-zA-Z0-9]{48,}/);
                                if (match) results.push(match[0]);
                            }
                        }
                    }
                }
            }
            
            // 方法2: 查找所有具有value属性的元素
            var inputElements = document.querySelectorAll('input, textarea');
            for (var i = 0; i < inputElements.length; i++) {
                var value = inputElements[i].value;
                if (value && value.includes('sk-')) {
                    var match = value.match(/sk-[a-zA-Z0-9]{48,}/);
                    if (match) results.push(match[0]);
                }
            }
            
            // 方法3: 查找所有带数据属性的元素
            var allWithData = document.querySelectorAll('[data-*]');
            for (var i = 0; i < allWithData.length; i++) {
                var el = allWithData[i];
                for (var j = 0; j < el.attributes.length; j++) {
                    var attr = el.attributes[j];
                    if (attr.name.startsWith('data-') && attr.value && attr.value.includes('sk-')) {
                        var match = attr.value.match(/sk-[a-zA-Z0-9]{48,}/);
                        if (match) results.push(match[0]);
                    }
                }
            }
            
            // 返回结果（优先返回最长的密钥）
            if (results.length > 0) {
                results.sort(function(a, b) { return b.length - a.length; });
                return results[0];
            }
            
            return null;
        })();
        """)
        
        if js_result and js_result.startswith("sk-") and len(js_result) >= 48:
            key_text = js_result
            print(f"[进程 {process_id}] 通过JavaScript从DOM中找到完整密钥！")
            return key_text
    except Exception as js_err:
        print(f"[进程 {process_id}] 通过JavaScript提取密钥失败: {js_err}")
    
    # 方法2: 分析页面源码
    try:
        page_source = driver.page_source
        sk_matches = re.findall(r'sk-[a-zA-Z0-9]{48,}', page_source)
        if sk_matches:
            key_text = max(sk_matches, key=len)
            print(f"[进程 {process_id}] 从页面源码中找到完整密钥！")
            return key_text
    except Exception as source_err:
        print(f"[进程 {process_id}] 从页面源码提取密钥失败: {source_err}")
    
    # 方法3: 分析可见元素的文本
    try:
        for selector in ['div', 'span', 'p', 'code', 'pre', 'td']:
            elements = driver.find_elements(By.TAG_NAME, selector)
            for element in elements:
                try:
                    text = element.text or element.get_attribute('textContent')
                    if text and 'sk-' in text:
                        matches = re.findall(r'sk-[a-zA-Z0-9]{48,}', text)
                        if matches:
                            key_text = max(matches, key=len)
                            print(f"[进程 {process_id}] 从元素文本中找到完整密钥！")
                            return key_text
                except:
                    continue
    except Exception as elem_err:
        print(f"[进程 {process_id}] 从元素文本提取密钥失败: {elem_err}")
    
    # 方法4: 尝试查找任何输入框中的sk值
    try:
        input_elements = driver.find_elements(By.TAG_NAME, 'input')
        for input_elem in input_elements:
            try:
                value = input_elem.get_attribute('value')
                if value and 'sk-' in value:
                    matches = re.findall(r'sk-[a-zA-Z0-9]{48,}', value)
                    if matches:
                        key_text = max(matches, key=len)
                        print(f"[进程 {process_id}] 从输入框中找到完整密钥！")
                        return key_text
            except:
                continue
    except Exception as input_err:
        print(f"[进程 {process_id}] 从输入框提取密钥失败: {input_err}")
    
    return key_text

if __name__ == "__main__":
    # 确保脚本使用多进程模式启动
    multiprocessing.freeze_support()
    
    # 在这里创建Manager实例
    manager = Manager()
    extracted_keys = manager.dict()
    
    # 检查是否已安装pyperclip
    if pyperclip is None:
        print("警告: 未找到pyperclip模块，无法访问系统剪贴板")
        print("请运行 'pip install pyperclip' 安装该模块以获取更好的密钥提取效果")
        print("继续运行脚本，但可能无法提取完整密钥...\n")
    
    # 注册退出时的清理函数
    def cleanup_wrapper():
        cleanup_temp_directories(extracted_keys)
    
    atexit.register(cleanup_wrapper)
    
    # 添加信号处理程序，确保在Ctrl+C时也能清理
    def signal_handler(sig, frame):
        print("\n接收到中断信号，准备清理...")
        cleanup_temp_directories(extracted_keys)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("SiliconFlow手机号自动填写工具 (多进程版)")
    print("=" * 50)
    print("请输入或粘贴包含手机号的文本")
    print("输入完成后，请键入'end'然后按回车结束输入")
    print("这样可以确保处理所有数据，即使其中包含空行")
    print("=" * 50)
    
    # 收集输入（直到遇到特定结束标记）
    lines = []
    print("请开始输入文本（输入'end'结束）：")
    while True:
        try:
            line = input()
            if line.strip() == "end":
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
    
    # 询问是否需要输入邀请码
    invitation_code = None
    invitation_prompt = input("\n是否需要输入邀请码？如需输入请输入邀请码，否则直接回车: ")
    if invitation_prompt.strip():
        invitation_code = invitation_prompt.strip()
        print(f"已设置邀请码: {invitation_code}")
    else:
        print("未设置邀请码")
    
    # 直接启动浏览器
    print(f"\n正在为 {len(phone_numbers)} 个手机号启动独立的浏览器进程...")
    processes = open_multiple_browsers(phone_numbers, sid, invitation_code, extracted_keys)
    
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
                
                # 如果有进程结束，保存已提取的密钥
                if len(extracted_keys) > 0:
                    save_api_keys(extracted_keys)
                
                processes = running_processes
                
            if not running_processes:
                print("所有浏览器进程已关闭，脚本结束")
                break
    except KeyboardInterrupt:
        print("\n主脚本已终止，浏览器进程会继续运行")
    finally:
        # 确保在任何情况下退出前都执行清理
        cleanup_temp_directories(extracted_keys)
    
    print("感谢使用！") 