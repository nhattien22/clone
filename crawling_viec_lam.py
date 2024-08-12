from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import sys
import time

# Thiết lập mã hóa đầu ra của hệ thống
sys.stdout.reconfigure(encoding='utf-8')

# Đường dẫn đến ChromeDriver
chrome_driver_path = r'C:\Users\kings\Downloads\chromedriver-win64\chromedriver.exe'

# Tùy chọn cho Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')  # Chạy Chrome ở chế độ ẩn

# Khởi tạo trình duyệt
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL của trang web bạn muốn crawl
base_url = 'https://www.vietnamworks.com/viec-lam-goi-y'

# Danh sách để lưu dữ liệu
data = []

# Hàm cuộn trang
def scroll_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Chờ trang tải thêm nội dung

# Định nghĩa số trang bạn muốn thu thập dữ liệu
num_pages = 10  # Hoặc sử dụng một cách để xác định số trang, nếu trang có nhiều trang hơn

for page in range(1, num_pages + 1):
    url = f'{base_url}?page={page}'
    driver.get(url)
    
    # Đợi một vài giây để trang web tải xong
    wait = WebDriverWait(driver, 20)  # Tăng thời gian chờ đợi
    try:
        # Cuộn trang để tải nội dung
        scroll_page(driver)

        job_elements = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.sc-bHnlcS.exLWkI.view_job_item.recommendation_jobs')))

        print(f"Found {len(job_elements)} job elements on page {page}")
        
        # Duyệt qua các phần tử và lấy nội dung của chúng
        for job_element in job_elements:
            try:
                job_title = job_element.find_element(By.CSS_SELECTOR, '.sc-gvPdwL.jmYUbh').text.strip()  # Thay đổi selector
                company_name = job_element.find_element(By.CSS_SELECTOR, '.sc-iLWXdy.beDjiy').text.strip()  # Thay đổi selector
                price = job_element.find_element(By.CSS_SELECTOR, '.sc-enkILE.jeOYnv').text.strip()
                location = job_element.find_element(By.CSS_SELECTOR, '.sc-bcSKrn.jwGMHn').text.strip()  # Thay đổi selector

                # Thêm dữ liệu vào danh sách
                data.append({
                    'Tên Công Việc': job_title,
                    'Tên Công Ty': company_name,
                    'Lương': price,
                    'Địa Điểm': location
                })
            except Exception as e:
                print(f"Error extracting data from job element on page {page}: {e}")
    except Exception as e:
        print(f"Error loading page {page}: {e}")

# Tạo DataFrame từ dữ liệu
df = pd.DataFrame(data)

# Lưu DataFrame vào file Excel
df.to_excel('jobs_goi_y.xlsx', index=False, engine='openpyxl')

# Đóng trình duyệt
driver.quit()
