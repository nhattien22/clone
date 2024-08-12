<?php
require 'vendor/autoload.php'; // Đảm bảo bạn đã cài đặt PHPSpreadsheet thông qua Composer

use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

// URL của trang web
$url = 'https://www.topcv.vn/viec-lam-tot-nhat';

function scrapeTopCvJobs($url)
{
    // Khởi tạo CURL
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // Bỏ qua SSL verification nếu cần thiết

    $response = curl_exec($ch);
    curl_close($ch);

    if ($response === false) {
        throw new Exception("Failed to fetch the page.");
    }

    // Phân tích nội dung của trang web
    $dom = new DOMDocument();
    @$dom->loadHTML($response);
    $xpath = new DOMXPath($dom);

    // Tìm tất cả các phần tử chứa thông tin công việc
    $job_elements = $xpath->query("//div[@class='job-item-default bg-highlight job-ta']");

    // Danh sách chứa thông tin công việc
    $jobs = [];
    foreach ($job_elements as $element) {
        $job_title = $xpath->query(".//h3[@class='title']", $element)->item(0);
        $company_name = $xpath->query(".//a[@class='company']", $element)->item(0);

        $jobs[] = [
            'title' => $job_title ? trim($job_title->textContent) : 'No title',
            'company_name' => $company_name ? trim($company_name->textContent) : 'No Company Name',
        ];
    }

    return $jobs;
}

// Kiểm tra phương thức yêu cầu
$requestMethod = $_SERVER['REQUEST_METHOD'] ?? 'CLI';

if ($requestMethod === 'GET' || $requestMethod === 'CLI') {
    try {
        $jobs = scrapeTopCvJobs($url);

        // Khởi tạo file Excel
        $spreadsheet = new Spreadsheet();
        $sheet = $spreadsheet->getActiveSheet();
        $sheet->setCellValue('A1', 'Tên công ty');
        $sheet->setCellValue('B1', 'Mô tả');

        // Ghi dữ liệu vào Excel
        $row = 2;
        foreach ($jobs as $job) {
            $sheet->setCellValue('A' . $row, $job['company_name']);
            $sheet->setCellValue('B' . $row, $job['title']);
            $row++;
        }

        $writer = new Xlsx($spreadsheet);
        $filename = 'Crawling_viec_lam.xlsx';
        $writer->save($filename);

        echo "Data has been written to $filename";
    } catch (Exception $e) {
        echo "An error occurred: " . $e->getMessage();
    }
} else {
    echo "This script can only be run via GET request or CLI.";
}
?>
