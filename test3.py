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
first_page_url = 'https://www.topcv.vn/viec-lam-tot-nhat'
base_url = 'https://www.topcv.vn/viec-lam-tot-nhat?page='

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

# Hàm để crawl dữ liệu từ các trang
def crawl_data():
    global data  # Đảm bảo sử dụng biến toàn cục để lưu dữ liệu

    # Định nghĩa số trang bạn muốn thu thập dữ liệu
    num_pages = 10  # Thay đổi số trang nếu cần

    for page in range(1, num_pages + 1):
        if page == 1:
            url = first_page_url
        else:
            url = f'{base_url}{page}'
        driver.get(url)
        
        # Đợi một vài giây để trang web tải xong
        wait = WebDriverWait(driver, 20)  # Tăng thời gian chờ đợi

        try:
            # Cuộn trang để tải nội dung
            scroll_page(driver)
            
            # Đợi cho các phần tử công việc xuất hiện
            job_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.job-item-default.bg-highlight.job-ta')))
            
            print(f"Found {len(job_elements)} job elements on page {page}")
            
            # Duyệt qua các phần tử và lấy nội dung của chúng
            for job_element in job_elements:
                try:
                    job_title = job_element.find_element(By.CSS_SELECTOR, '.title').text.strip()  # Thay đổi selector nếu cần
                    company_name = job_element.find_element(By.CSS_SELECTOR, '.company').text.strip()  # Thay đổi selector nếu cần
                    price = job_element.find_element(By.CSS_SELECTOR, '.title-salary').text.strip()
                    location = job_element.find_element(By.CSS_SELECTOR, '.address').text.strip()  # Thay đổi selector nếu cần
                    image = job_element.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')

                    # Thêm dữ liệu vào danh sách
                    data.append({
                        'Tên Công Việc': job_title,
                        'Tên Công Ty': company_name,
                        'Lương': price,
                        'Địa Điểm': location,
                        'Hình Ảnh': image
                    })
                except Exception as e:
                    print(f"Error extracting data from job element on page {page}: {e}")
        except Exception as e:
            print(f"Error loading page {page}: {e}")

# Vòng lặp vô hạn để crawl dữ liệu sau mỗi 5 phút
while True:
    print("Starting crawl...")
    crawl_data()
    
    # Lưu dữ liệu vào file CSV
    df = pd.DataFrame(data)
    df.to_csv('jobs_all_new.csv', index=False, encoding='utf-8-sig')
    
    # print("Data saved. Sleeping for 5 minutes...")
    # time.sleep(300)  # Chờ 5 phút (300 giây) trước khi thực hiện crawl tiếp
