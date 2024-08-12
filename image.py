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
first_page_url = 'https://www.vietnamworks.com/tim-viec-lam/tim-tat-ca-viec-lam'
base_url = 'https://www.vietnamworks.com/viec-lam?page='

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
num_pages = 1  # Thay đổi số trang nếu cần

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
        job_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.search_list.view_job_item')))
        
        print(f"Found {len(job_elements)} job elements on page {page}")
        
        # Duyệt qua các phần tử và lấy nội dung của chúng
        for job_element in job_elements:
            try:
                job_title = job_element.find_element(By.CSS_SELECTOR, '.sc-hXCwRK').text.strip()
                company_name = job_element.find_element(By.CSS_SELECTOR, '.sc-biptUy').text.strip()
                price = job_element.find_element(By.CSS_SELECTOR, '.sc-kzkBiZ').text.strip()
                location = job_element.find_element(By.CSS_SELECTOR, '.sc-cdaca-d').text.strip()
                job_elements_details = job_element.find_elements(By.CSS_SELECTOR, '.sc-fHsjty.hFWMKy')

                # Lấy URL của hình ảnh
                try:
                    image_element = job_element.find_element(By.CSS_SELECTOR, 'img')
                    image_url = image_element.get_attribute('src') if image_element else 'No Image'
                except Exception as e:
                    image_url = 'No Image'
                    print(f"Error extracting image URL: {e}")

                # Ghép các phần tử job lại với nhau bằng dấu gạch nối
                job = ' - '.join([elem.text.strip() for elem in job_elements_details])

                # Kiểm tra nếu không phải là "+2", "+3"
                if "+2" not in job_title and "+3" not in job_title:
                    # Thêm dữ liệu vào danh sách
                    data.append({
                        'Tên Công Việc': job_title,
                        'Tên Công Ty': company_name,
                        'Lương': price,
                        'Địa Điểm': location,
                        'Công Việc': job,
                        'Hình Ảnh': image_url
                    })
            except Exception as e:
                print(f"Error extracting data from job element on page {page}: {e}")
    except Exception as e:
        print(f"Error loading page {page}: {e}")

# Tạo DataFrame từ dữ liệu
df = pd.DataFrame(data)

# Lưu DataFrame vào file Excel
df.to_excel('jobs_allssss.xlsx', index=False, engine='openpyxl')

# Đóng trình duyệt
driver.quit()
