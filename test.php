<?php
require 'vendor/autoload.php';
require 'phpquery-1.2.0\classes\php-query.php'; // Đảm bảo bạn có đúng đường dẫn đến file phpQuery.php

use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

// URL của trang web
$url = 'https://www.vietnamworks.com/';

// Hàm lấy dữ liệu từ trang web
function scrape_job_data($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);
    curl_close($ch);

    if ($response === false) {
        throw new Exception("Failed to fetch the page.");
    }

    // Tạo đối tượng phpQuery để phân tích HTML
    $doc = phpQuery::newDocument($response);

    // Sử dụng phpQuery để tìm tất cả các phần tử với lớp 'swiper-slide'
    $elements = $doc->find('.swiper-container');

    if ($elements->length === 0) {
        throw new Exception("No elements found with the provided class.");
    }

    $data = [];

    foreach ($elements as $element) {
        $pqElement = pq($element);
        // Lấy toàn bộ HTML của phần tử
        $data[] = $pqElement->html();
    }

    return $data;
}

// Lấy dữ liệu
$data = scrape_job_data($url);

// Tạo file Excel
$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();
$sheet->setCellValue('A1', 'HTML Content');

// Ghi dữ liệu vào file Excel
$row = 2;
foreach ($data as $item) {
    // Ghi dữ liệu vào từng ô, có thể bạn muốn tùy chỉnh cách dữ liệu được ghi vào
    $sheet->setCellValue('A' . $row, $item);
    $row++;
}

// Lưu file Excel
$writer = new Xlsx($spreadsheet);
$writer->save('danhsach_congviec.xlsx');

echo "Data has been written to danhsach_congviec.xlsx";
?>
