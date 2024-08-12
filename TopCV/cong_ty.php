<?php
// Cài đặt đường dẫn tới thư viện PhpSpreadsheet
require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

// URL của trang web
$url = 'https://www.topcv.vn/cong-ty';

// Hàm lấy dữ liệu từ trang web
function scrape_pyan_cong_ty($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);
    curl_close($ch);

    if ($response === false) {
        throw new Exception("Failed to fetch the page.");
    }

    // Tạo đối tượng DOMDocument để phân tích HTML
    $dom = new DOMDocument();
    @$dom->loadHTML($response);

    $xpath = new DOMXPath($dom);
    $elements = $xpath->query("//div[contains(@class, 'col-md-4') and contains(@class, 'col-sm-6')]");

    $companies = [];

    foreach ($elements as $element) {
        $company_name = '';
        $company_description = '';
        $company_logo = '';

        // Lấy tên công ty
        $nameNode = $xpath->query(".//a[contains(@class, 'company-name')]", $element);
        if ($nameNode && $nameNode->length > 0) {
            $company_name = trim($nameNode->item(0)->textContent);
        } else {
            $company_name = 'No name';
        }

        // Lấy mô tả công ty
        $descriptionNode = $xpath->query(".//div[contains(@class, 'company-description')]", $element);
        if ($descriptionNode && $descriptionNode->length > 0) {
            $company_description = trim($descriptionNode->item(0)->textContent);
        } else {
            $company_description = 'No description';
        }

        // Lấy logo công ty
        $logoNode = $xpath->query(".//div[contains(@class, 'company-logo')]", $element);
        if ($logoNode && $logoNode->length > 0) {
            $company_logo = trim($logoNode->item(0)->textContent);
        } else {
            $company_logo = 'No logo';
        }

        $companies[] = [
            'company_name' => $company_name,
            'company_description' => $company_description,
            'company_logo' => $company_logo
        ];
    }

    return $companies;
}

// Lấy dữ liệu
$companies = scrape_pyan_cong_ty($url);

// Tạo file Excel
$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();
$sheet->setCellValue('A1', 'Tên công ty');
$sheet->setCellValue('B1', 'Mô tả');
$sheet->setCellValue('C1', 'Logo');

// Ghi dữ liệu vào file Excel
$row = 2;
foreach ($companies as $company) {
    $sheet->setCellValue('A' . $row, $company['company_name']);
    $sheet->setCellValue('B' . $row, $company['company_description']);
    $sheet->setCellValue('C' . $row, $company['company_logo']);
    $row++;
}

// Lưu file Excel
$writer = new Xlsx($spreadsheet);
$writer->save('Crawling.xlsx');

echo "Data has been written to Crawling.xlsx";
?>
