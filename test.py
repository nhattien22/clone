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
chrome_options.add_argument('--disable-gpu')  # Vô hiệu hóa GPU
chrome_options.add_argument('--no-sandbox')  # Thêm tùy chọn no-sandbox
chrome_options.add_argument('--disable-dev-shm-usage')  # Thêm tùy chọn disable-dev-shm-usage

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

# Định nghĩa số trang bạn muốn thu thập dữ liệu
num_pages = 10  # Thay đổi số trang nếu cần

for page in range(1, num_pages + 1):
    if page == 1:
        url = first_page_url
    else:
        url = f'{base_url}{page}'
    driver.get(url)
    
    # Đợi một vài giây để trang web tải xong
    wait = WebDriverWait(driver, 60)  # Tăng thời gian chờ đợi lên 60 giây

    try:
        # Cuộn trang để tải nội dung
        scroll_page(driver)
        
        # Đợi cho các phần tử công việc xuất hiện
        job_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.job-item-default.bg-highlight.job-ta')))
        
        print(f"Found {len(job_elements)} job elements on page {page}")

        # Duyệt qua các phần tử và lấy nội dung của chúng
        for job_element in job_elements:
            try:
                # Sử dụng các selector cần thiết
                job_title_selector = '.title'
                company_name_selector = '.company'
                price_selector = '.title-salary'
                location_selector = '.address'
                description_selector = '.sc-4913d170-6.hITvKb'
                job_link_selector = 'a'
                
                # Lấy dữ liệu từ các phần tử
                try:
                    job_title = job_element.find_element(By.CSS_SELECTOR, job_title_selector).text.strip()
                except Exception as e:
                    print(f"Error retrieving job title using selector {job_title_selector}: {e}")
                    job_title = "N/A"
                
                try:
                    company_name = job_element.find_element(By.CSS_SELECTOR, company_name_selector).text.strip()
                except Exception as e:
                    print(f"Error retrieving company name using selector {company_name_selector}: {e}")
                    company_name = "N/A"
                
                try:
                    price = job_element.find_element(By.CSS_SELECTOR, price_selector).text.strip()
                except Exception as e:
                    print(f"Error retrieving price using selector {price_selector}: {e}")
                    price = "N/A"
                
                try:
                    location = job_element.find_element(By.CSS_SELECTOR, location_selector).text.strip()
                except Exception as e:
                    print(f"Error retrieving location using selector {location_selector}: {e}")
                    location = "N/A"

                # Nhấp vào tiêu đề công việc để mở trang chi tiết
                try:
                    job_link = job_element.find_element(By.CSS_SELECTOR, job_link_selector)
                    job_url = job_link.get_attribute('href')  # Lấy URL của liên kết công việc
                    job_link.click()  # Nhấp vào liên kết công việc
                    
                    # In thông báo với URL của trang chi tiết công việc
                    print(f"Clicked on job title: {job_title}")
                    print(f"Navigated to: {job_url}")
                except Exception as e:
                    print(f"Error clicking job link using selector {job_link_selector}: {e}")
                    continue

                # Đợi trang chi tiết công việc tải xong
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, description_selector)))
                    print(f"Successfully loaded job description for: {job_title}")
                except Exception as e:
                    print(f"Error waiting for description using selector {description_selector}: {e}")
                    continue
                
                # Lấy thông tin mô tả công việc
                try:
                    description_element = driver.find_element(By.CSS_SELECTOR, description_selector)
                    paragraphs = description_element.find_elements(By.TAG_NAME, 'p')
                    job_description = "\n".join([p.text.strip() for p in paragraphs])
                    
                    # Thêm dữ liệu vào danh sách
                    data.append({
                        'Tên Công Việc': job_title,
                        'Tên Công Ty': company_name,
                        'Lương': price,
                        'Địa Điểm': location,
                        'Mô Tả Công Việc': job_description
                    })

                    # In ra thông tin khi đã nhấp vào liên kết và lấy dữ liệu thành công
                    print(f"Successfully extracted data for job title: {job_title}")
                    print(f"Description: {job_description[:200]}...")  # In ra một phần mô tả để kiểm tra
                except Exception as e:
                    print(f"Error retrieving job description using selector {description_selector}: {e}")

                # Quay lại trang danh sách công việc
                driver.back()
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.search_list.view_job_item')))  # Chờ trang danh sách tải lại

            except Exception as e:
                print(f"Error extracting data from job element on page {page}: {e}")
                # Quay lại trang danh sách công việc nếu gặp lỗi
                driver.back()
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.search_list.view_job_item')))  # Chờ trang danh sách tải lại nếu có lỗi
                continue  # Bỏ qua phần tử gặp lỗi và tiếp tục với phần tử tiếp theo
    except Exception as e:
        print(f"Error loading page {page}: {e}")

# Tạo DataFrame từ dữ liệu
df = pd.DataFrame(data)

# Lưu DataFrame vào file Excel
df.to_excel('jobs_allsss.xlsx', index=False, engine='openpyxl')

# Đóng trình duyệt
driver.quit()
