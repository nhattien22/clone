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
first_page_url = 'https://www.vietnamworks.com/viec-lam-quan-ly?utm_source_navi=header&utm_medium_navi=managementjobs'
base_url = 'https://www.vietnamworks.com/viec-lam-quan-ly'

# Danh sách để lưu dữ liệu
data = []

# Hàm cuộn trang
def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Chờ trang tải thêm nội dung
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Định nghĩa số trang bạn muốn thu thập dữ liệu
num_pages = 10  # Thay đổi số trang nếu cần

# Hàm để kiểm tra và tránh lặp lại dữ liệu
def extract_job_data(job_element):
    job_title = job_element.find_element(By.CSS_SELECTOR, '.sc-hkaVUD.knwNkd').text.strip()  # Thay đổi selector nếu cần
    company_name = job_element.find_element(By.CSS_SELECTOR, '.sc-biptUy.hHQqla').text.strip()  # Thay đổi selector nếu cần
    salary = job_element.find_element(By.CSS_SELECTOR, '.sc-eZuMGc.emCAmk').text.strip()
    location = job_element.find_element(By.CSS_SELECTOR, '.sc-cdaca-d.hZiGVD').text.strip()  # Thay đổi selector nếu cần

    job_data = {
        'Tên Công Việc': job_title,
        'Tên Công Ty': company_name,
        'Lương': salary,
        'Địa Điểm': location
    }
    
    # Kiểm tra xem dữ liệu này đã tồn tại chưa
    if job_data not in data:
        data.append(job_data)

for page in range(1, num_pages + 1):
    if page == 1:
        url = first_page_url
    else:
        url = f'{base_url}?page={page}'
    driver.get(url)
    
    # Đợi một vài giây để trang web tải xong
    wait = WebDriverWait(driver, 20)  # Tăng thời gian chờ đợi
    
    try:
        # Đợi trang web tải xong phần tử cụ thể để đảm bảo nội dung đã được tải mới
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.search_list.view_job_item')))
        
        # Cuộn trang để tải nội dung
        scroll_page(driver)
        
        # Tìm tất cả các phần tử công việc
        job_elements = driver.find_elements(By.CSS_SELECTOR, '.search_list.view_job_item')
        
        print(f"Found {len(job_elements)} job elements on page {page}")
        
        # Duyệt qua các phần tử và lấy nội dung của chúng
        for job_element in job_elements:
            try:
                extract_job_data(job_element)
            except Exception as e:
                print(f"Error extracting data from job element on page {page}: {e}")
    except Exception as e:
        print(f"Error loading page {page}: {e}")

# Tạo DataFrame từ dữ liệu
df = pd.DataFrame(data)

# Lưu DataFrame vào file Excel
df.to_excel('jobs_quan_ly.xlsx', index=False, engine='openpyxl')

# Đóng trình duyệt
driver.quit()
