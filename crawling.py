import sys
import requests
from bs4 import BeautifulSoup
import json
import xlwings as xw  # Nhập thư viện xlwings

# Thiết lập mã hóa đầu ra của hệ thống
sys.stdout.reconfigure(encoding='utf-8')

# URL của trang web
url = 'https://www.topcv.vn/cong-ty'

def scrape_pyan_cong_ty(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch the page.")
    # Phân tích nội dung của trang web bằng BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Tìm tất cả các phần tử chứa thông tin công ty
    course_elements = soup.find_all("div", class_="col-md-4 col-sm-6")

    # Danh sách chứa thông tin công ty
    course = []
    for element in course_elements:
        company_name = element.find("a", class_="company-name").text.strip() if element.find("a", class_="company-name") else 'No name'
        company_description = element.find("div", class_="company-description").text.strip() if element.find("div", class_="company-description") else 'No description'
        # Thêm thông tin công ty vào danh sách
        course.append({
            'company_name': company_name,
            'company-description': company_description
        })

    return course

if __name__ == "__main__":
    courses = scrape_pyan_cong_ty(url)
    wb = xw.Book()
    sheet = wb.sheets.active

    sheet.range("A1").value = "Tên công ty"
    sheet.range("B1").value = "Mô tả"

    for idx, courses in enumerate(courses, start=1):
        row = idx + 1
        sheet.range(f"A{row}").value = courses['company_name']
        sheet.range(f"B{row}").value = courses['company-description']

    wb.save("Crawlingsssssss.xlsx")
    wb.close()

#     for idx, course in enumerate(courses, start=1):
#         print(f"Công ty {idx}:")
#         print(f"Tên công ty: {course['company_name']}")
#         print(f"Mô tả: {course['company_description']}")
#         print()

# # # Ghi kết quả vào file với mã hóa UTF-8
# #     with open('companies.json', 'w', encoding='utf-8') as f:
# #         json.dump(courses, f, ensure_ascii=False, indent=4)

# #     print("Data has been written to companies.json")