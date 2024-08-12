<?php
require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

$url = 'https://viecoi.vn/tim-viec/all.html';

function scrape_pyan_viec_lam($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);
    curl_close($ch);

    if ($response === false) {
        throw new Exception("Failed to fetch the page");
    }

    $dom = new DOMDocument();
    @$dom->loadHTML($response);

    $xpath = new DOMXPath($dom);
    // Sửa biểu thức XPath để đúng cú pháp
    $elements = $xpath->query("//div[contains(@class, 'list_job_detail')]");

    $companies = [];

    foreach ($elements as $element) {
        $job_name = '';
        // Sửa biểu thức XPath để chọn đúng phần tử
        $namejobNode = $xpath->query(".//a[contains(@class, 'line-clamp-2')]", $element);
        if ($namejobNode && $namejobNode->length > 0) {
            $job_name = trim($namejobNode->item(0)->textContent);
        } else {
            $job_name = 'No job name';
        }

        $companies[] = [
            'Job Name' => $job_name,
        ];
    }
    return $companies;
}

$companies = scrape_pyan_viec_lam($url);
$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();
$sheet->setCellValue('A1', 'Job Name');

$row = 2;
foreach ($companies as $company) {
    $sheet->setCellValue('A' . $row, $company['Job Name']);
    $row++;
}

$writer = new Xlsx($spreadsheet); // Sửa lỗi chính tả
$writer->save('viecoi.xlsx');
echo "Data has been written to viecoi.xlsx";
?>
