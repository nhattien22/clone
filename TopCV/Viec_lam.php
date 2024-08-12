<?php
require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

$url = 'https://www.topcv.vn/viec-lam-tot-nhat';

function scrape_pyan_viec_lam($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);
    curl_close($ch);

    if ($response === false) {
        throw new Exception("Failed to fetch the page.");
    }

    $dom = new DOMDocument();
    @$dom->loadHTML($response);

    $xpath = new DOMXPath($dom);
    // Sửa biểu thức XPath để đúng cú pháp
    $elements = $xpath->query("//div[contains(@class, 'job-item-default') and contains(@class, 'bg-highlight') and contains(@class, 'job-ta')]");

    $jobs = [];

    foreach ($elements as $element) {
        $job_title = '';
        $company_name = '';
        $posted_time = '';

        // Lấy tên công việc
        $titleNode = $xpath->query(".//div[@class='body-content']//h3[@class='title']/a", $element);
        if ($titleNode && $titleNode->length > 0) {
            $job_title = trim($titleNode->item(0)->textContent);
        } else {
            $job_title = 'No Job Title';
        }

        // Lấy tên công ty
        $companyNode = $xpath->query(".//a[contains(@class, 'company')]", $element);
        if ($companyNode && $companyNode->length > 0) {
            $company_name = trim($companyNode->item(0)->textContent);
        } else {
            $company_name = 'No Company Name';
        }

        // Lấy thời gian đăng
        $timeNode = $xpath->query(".//div[contains(@class, 'label-content')]//span[contains(@class, 'address')]", $element);
        if ($timeNode && $timeNode->length > 0) {
            $posted_time = trim($timeNode->item(0)->textContent);
        } else {
            $posted_time = 'No Posted Time';
        }

        $jobs[] = [
            'Job Title' => $job_title,
            'Company Name' => $company_name,
            'Posted Time' => $posted_time,
        ];
    }
    return $jobs;
}

$jobs = scrape_pyan_viec_lam($url);

$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();
$sheet->setCellValue('A1', 'Tên Công Việc');
$sheet->setCellValue('B1', 'Tên Công Ty');
$sheet->setCellValue('C1', 'Thời Gian Đăng');

$row = 2;
foreach ($jobs as $job) {
    $sheet->setCellValue('A' . $row, $job['Job Title']);
    $sheet->setCellValue('B' . $row, $job['Company Name']);
    $sheet->setCellValue('C' . $row, $job['Posted Time']);
    $row++;
}

$writer = new Xlsx($spreadsheet);
$writer->save('job.xlsx');
echo "Data has been written to job.xlsx";
?>
