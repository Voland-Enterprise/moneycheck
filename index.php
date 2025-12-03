<?php
// CLI script to enrich domains with Ahrefs and Moz metrics.
// Usage example:
// php index.php --input domains.xlsx --output enriched.xlsx --domain-column=domain

ini_set('display_errors', 'stderr');

function loadEnvFile(string $path = '.env'): void
{
    if (!file_exists($path)) {
        return;
    }

    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (str_starts_with(trim($line), '#') || !str_contains($line, '=')) {
            continue;
        }
        [$name, $value] = array_map('trim', explode('=', $line, 2));
        if ($name !== '' && getenv($name) === false) {
            putenv("{$name}={$value}");
        }
    }
}

function normalizeDomain(string $domain, bool $stripWww = false): string
{
    $domain = trim(strtolower($domain));
    $domain = preg_replace('#^https?://#', '', $domain);
    $domain = preg_replace('#/.*$#', '', $domain);
    if ($stripWww) {
        $domain = preg_replace('#^www\\.#', '', $domain);
    }
    return $domain;
}

function logMessage(string $message): void
{
    fwrite(STDERR, $message . PHP_EOL);
}

function detectCsvDelimiter(string $path): string
{
    $sample = file_get_contents($path, false, null, 0, 2048);
    $candidates = [',', ';', '\t'];
    $best = ',';
    $bestCount = 0;
    foreach ($candidates as $delimiter) {
        $count = substr_count($sample, $delimiter);
        if ($count > $bestCount) {
            $bestCount = $count;
            $best = $delimiter;
        }
    }
    return $best;
}

function readCsv(string $path, ?string $delimiter = null): array
{
    $delimiter = $delimiter ?: detectCsvDelimiter($path);
    if (($handle = fopen($path, 'r')) === false) {
        throw new RuntimeException("Cannot open CSV file: {$path}");
    }

    $rows = [];
    while (($data = fgetcsv($handle, 0, $delimiter)) !== false) {
        $rows[] = $data;
    }
    fclose($handle);
    return $rows;
}

function writeCsv(string $path, array $rows, string $delimiter = ','): void
{
    $handle = fopen($path, 'w');
    foreach ($rows as $row) {
        fputcsv($handle, $row, $delimiter);
    }
    fclose($handle);
}

function columnIndexToName(int $index): string
{
    $name = '';
    $index++;
    while ($index > 0) {
        $remainder = ($index - 1) % 26;
        $name = chr(65 + $remainder) . $name;
        $index = (int)(($index - 1) / 26);
    }
    return $name;
}

function parseXlsxSheet(string $xlsxPath, ?string $sheetName = null): array
{
    $zip = new ZipArchive();
    if ($zip->open($xlsxPath) !== true) {
        throw new RuntimeException("Cannot open XLSX file: {$xlsxPath}");
    }

    $workbookXml = $zip->getFromName('xl/workbook.xml');
    if ($workbookXml === false) {
        throw new RuntimeException('Invalid XLSX: workbook.xml missing');
    }
    $workbook = new SimpleXMLElement($workbookXml);
    $sheets = [];
    foreach ($workbook->sheets->sheet as $sheet) {
        $attrs = $sheet->attributes();
        $sheets[(string) $attrs['name']] = (string) $attrs['r:id'];
    }
    $relsXml = $zip->getFromName('xl/_rels/workbook.xml.rels');
    if ($relsXml === false) {
        throw new RuntimeException('Invalid XLSX: workbook relationships missing');
    }
    $rels = new SimpleXMLElement($relsXml);
    $sheetPath = null;
    $targetSheet = $sheetName && isset($sheets[$sheetName]) ? $sheetName : array_key_first($sheets);
    $relationshipId = $sheets[$targetSheet];
    foreach ($rels->Relationship as $rel) {
        if ((string) $rel['Id'] === $relationshipId) {
            $sheetPath = 'xl/' . (string) $rel['Target'];
            break;
        }
    }
    if (!$sheetPath) {
        throw new RuntimeException('Unable to locate sheet data');
    }

    $sharedStrings = [];
    if (($shared = $zip->getFromName('xl/sharedStrings.xml')) !== false) {
        $sharedXml = new SimpleXMLElement($shared);
        foreach ($sharedXml->si as $idx => $si) {
            $sharedStrings[(int) $idx] = (string) $si->t;
        }
    }

    $sheetXml = $zip->getFromName($sheetPath);
    if ($sheetXml === false) {
        throw new RuntimeException('Sheet XML missing');
    }
    $sheet = new SimpleXMLElement($sheetXml);
    $rows = [];
    foreach ($sheet->sheetData->row as $row) {
        $current = [];
        foreach ($row->c as $cell) {
            $cellRef = (string) $cell['r'];
            preg_match('/([A-Z]+)([0-9]+)/', $cellRef, $matches);
            $col = $matches[1] ?? 'A';
            $colIndex = 0;
            for ($i = 0; $i < strlen($col); $i++) {
                $colIndex = $colIndex * 26 + (ord($col[$i]) - 64);
            }
            $colIndex--;
            $value = '';
            $type = (string) $cell['t'];
            if ($type === 's') {
                $idx = (int) $cell->v;
                $value = $sharedStrings[$idx] ?? '';
            } elseif ($type === 'inlineStr') {
                $value = (string) $cell->is->t;
            } else {
                $value = isset($cell->v) ? (string) $cell->v : '';
            }
            $current[$colIndex] = $value;
        }
        ksort($current);
        $rows[] = array_values($current);
    }
    $zip->close();
    return $rows;
}

function writeXlsx(string $path, array $rows): void
{
    $zip = new ZipArchive();
    if ($zip->open($path, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) {
        throw new RuntimeException("Cannot create XLSX: {$path}");
    }

    $zip->addFromString('[Content_Types].xml', <<<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
    <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
    <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
    <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>
XML);

    $zip->addFromString('_rels/.rels', <<<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
XML);

    $zip->addFromString('docProps/app.xml', <<<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
    <Application>PHP Script</Application>
</Properties>
XML);

    $zip->addFromString('docProps/core.xml', <<<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>Enriched domains</dc:title>
</cp:coreProperties>
XML);

    $zip->addFromString('xl/_rels/workbook.xml.rels', <<<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>
XML);

    $zip->addFromString('xl/workbook.xml', <<<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <sheets>
        <sheet name="Sheet1" sheetId="1" r:id="rId1"/>
    </sheets>
</workbook>
XML);

    $sheetData = "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData>";
    foreach ($rows as $rowIndex => $row) {
        $sheetData .= '<row r="' . ($rowIndex + 1) . '">';
        foreach (array_values($row) as $colIndex => $value) {
            $cellRef = columnIndexToName($colIndex) . ($rowIndex + 1);
            $escaped = htmlspecialchars((string) $value, ENT_XML1);
            $sheetData .= '<c r="' . $cellRef . '" t="inlineStr"><is><t>' . $escaped . '</t></is></c>';
        }
        $sheetData .= '</row>';
    }
    $sheetData .= '</sheetData></worksheet>';
    $zip->addFromString('xl/worksheets/sheet1.xml', $sheetData);

    $zip->close();
}

function getAhrefsMetrics(string $domain, array $config): array
{
    $token = $config['AHREFS_API_TOKEN'] ?? null;
    if (!$token) {
        logMessage("Ahrefs token missing; skipping domain {$domain}");
        return ['dr' => '', 'pr' => '', 'keywords' => ''];
    }

    $baseUrl = $config['AHREFS_BASE_URL'] ?? 'https://apiv2.ahrefs.com';
    $params = [
        'from' => 'domain_rating',
        'target' => $domain,
        'mode' => 'domain',
        'output' => 'json',
        'token' => $token,
        'select' => 'domain_rating,ur,keywords'
    ];
    $response = apiRequest($baseUrl, $params, [], $config);
    if (!$response) {
        return ['dr' => '', 'pr' => '', 'keywords' => ''];
    }

    $dr = $response['domain_rating'] ?? '';
    $pr = $response['ur'] ?? '';
    $keywords = $response['keywords'] ?? '';
    return ['dr' => $dr, 'pr' => $pr, 'keywords' => $keywords];
}

function getMozMetrics(string $domain, array $config): array
{
    $accessId = $config['MOZ_ACCESS_ID'] ?? null;
    $secretKey = $config['MOZ_SECRET_KEY'] ?? null;
    if (!$accessId || !$secretKey) {
        logMessage("Moz credentials missing; skipping domain {$domain}");
        return ['da' => '', 'pa' => ''];
    }

    $endpoint = ($config['MOZ_BASE_URL'] ?? 'https://lsapi.seomoz.com') . '/v2/url_metrics';
    $payload = json_encode([
        'targets' => [$domain],
        'metrics' => ['domain_authority', 'page_authority']
    ]);

    $headers = [
        'Content-Type: application/json',
        'Authorization: Basic ' . base64_encode($accessId . ':' . $secretKey)
    ];

    $response = apiRequest($endpoint, [], $headers, $config, $payload, 'POST');
    if (!$response || !isset($response['results'][0])) {
        return ['da' => '', 'pa' => ''];
    }
    $result = $response['results'][0];
    return [
        'da' => $result['domain_authority'] ?? '',
        'pa' => $result['page_authority'] ?? ''
    ];
}

function apiRequest(string $url, array $query, array $headers, array $config, ?string $body = null, string $method = 'GET')
{
    $retries = 3;
    $delayMs = (int) ($config['REQUEST_DELAY_MS'] ?? 500);
    $retryDelay = (int) ($config['RETRY_DELAY_MS'] ?? 1000);

    $attempt = 0;
    do {
        $attempt++;
        $fullUrl = $url . (empty($query) ? '' : ('?' . http_build_query($query)));
        $ch = curl_init($fullUrl);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 20);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $body ?? '');
        }

        $raw = curl_exec($ch);
        $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);

        usleep($delayMs * 1000);

        if ($raw === false || $status >= 500 || $status === 429) {
            logMessage("API request failed (status {$status}) attempt {$attempt}: {$error}");
            if ($attempt < $retries) {
                usleep($retryDelay * 1000 * $attempt);
                continue;
            }
            return null;
        }

        $decoded = json_decode($raw, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            logMessage('Failed to decode API response: ' . json_last_error_msg());
            return null;
        }

        if ($status >= 400) {
            logMessage("API returned error status {$status}: {$raw}");
            return null;
        }

        return $decoded;
    } while ($attempt < $retries);

    return null;
}

function buildOutputPath(string $input, ?string $output): string
{
    if ($output) {
        return $output;
    }
    $info = pathinfo($input);
    $dir = $info['dirname'] ?? '.';
    $name = $info['filename'] ?? 'output';
    $ext = isset($info['extension']) ? ('.' . $info['extension']) : '';
    return rtrim($dir, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR . $name . '_with_metrics' . $ext;
}

function appendMetrics(array $rows, string $domainColumn, callable $fetchAhrefs, callable $fetchMoz, bool $stripWww, ?int $limit = null): array
{
    if (empty($rows)) {
        return $rows;
    }

    $header = $rows[0];
    $columnIndex = array_search($domainColumn, $header, true);
    if ($columnIndex === false) {
        throw new RuntimeException("Domain column '{$domainColumn}' not found");
    }

    $newColumns = ['Ahrefs_DR', 'Ahrefs_PR', 'Ahrefs_Keywords', 'Moz_DA', 'Moz_PA'];
    $existing = array_flip($header);
    foreach ($newColumns as $col) {
        if (!isset($existing[$col])) {
            $header[] = $col;
        } else {
            // Ensure overwrite by keeping position
        }
    }

    $cache = [];
    $result = [$header];
    $totalRows = count($rows) - 1;
    $processed = 0;

    for ($i = 1; $i < count($rows); $i++) {
        if ($limit !== null && $processed >= $limit) {
            break;
        }
        $row = $rows[$i];
        $domainRaw = $row[$columnIndex] ?? '';
        $normalized = normalizeDomain($domainRaw, $stripWww);
        if ($normalized === '') {
            logMessage("Skipping empty domain at row {$i}");
            $normalized = '';
        }

        if (!isset($cache[$normalized])) {
            logMessage('Processing ' . ($processed + 1) . '/' . $totalRows . ': ' . $normalized);
            $ahrefs = $normalized ? $fetchAhrefs($normalized) : ['dr' => '', 'pr' => '', 'keywords' => ''];
            $moz = $normalized ? $fetchMoz($normalized) : ['da' => '', 'pa' => ''];
            $cache[$normalized] = [$ahrefs, $moz];
        } else {
            [$ahrefs, $moz] = $cache[$normalized];
        }

        $rowData = array_fill(0, count($header), '');
        foreach ($header as $idx => $name) {
            if ($name === 'Ahrefs_DR') {
                $rowData[$idx] = $cache[$normalized][0]['dr'] ?? '';
            } elseif ($name === 'Ahrefs_PR') {
                $rowData[$idx] = $cache[$normalized][0]['pr'] ?? '';
            } elseif ($name === 'Ahrefs_Keywords') {
                $rowData[$idx] = $cache[$normalized][0]['keywords'] ?? '';
            } elseif ($name === 'Moz_DA') {
                $rowData[$idx] = $cache[$normalized][1]['da'] ?? '';
            } elseif ($name === 'Moz_PA') {
                $rowData[$idx] = $cache[$normalized][1]['pa'] ?? '';
            } elseif (isset($rows[0][$idx])) {
                $rowData[$idx] = $row[$idx] ?? '';
            }
        }

        $result[] = $rowData;
        $processed++;
    }

    return $result;
}

function main(array $argv): void
{
    loadEnvFile();
    $options = getopt('', ['input:', 'output::', 'domain-column::', 'sheet::', 'delimiter::', 'limit::', 'strip-www::']);
    if (empty($options['input'])) {
        fwrite(STDERR, "Usage: php index.php --input <file> [--output <file>] [--domain-column <name>] [--sheet <name>] [--delimiter ,] [--limit N]\n");
        exit(1);
    }

    $input = $options['input'];
    $domainColumn = $options['domain-column'] ?? 'domain';
    $sheet = $options['sheet'] ?? null;
    $delimiter = $options['delimiter'] ?? null;
    $limit = isset($options['limit']) ? (int) $options['limit'] : null;
    $stripWww = isset($options['strip-www']) ? filter_var($options['strip-www'], FILTER_VALIDATE_BOOL) : false;
    $output = buildOutputPath($input, $options['output'] ?? null);

    $ext = strtolower(pathinfo($input, PATHINFO_EXTENSION));
    if (!in_array($ext, ['csv', 'xlsx'], true)) {
        throw new RuntimeException('Unsupported file format. Use CSV or XLSX.');
    }

    $rows = $ext === 'csv' ? readCsv($input, $delimiter) : parseXlsxSheet($input, $sheet);

    $config = [
        'AHREFS_API_TOKEN' => getenv('AHREFS_API_TOKEN') ?: null,
        'MOZ_ACCESS_ID' => getenv('MOZ_ACCESS_ID') ?: null,
        'MOZ_SECRET_KEY' => getenv('MOZ_SECRET_KEY') ?: null,
        'AHREFS_BASE_URL' => getenv('AHREFS_BASE_URL') ?: null,
        'MOZ_BASE_URL' => getenv('MOZ_BASE_URL') ?: null,
        'REQUEST_DELAY_MS' => getenv('REQUEST_DELAY_MS') ?: null,
        'RETRY_DELAY_MS' => getenv('RETRY_DELAY_MS') ?: null,
    ];

    $enriched = appendMetrics(
        $rows,
        $domainColumn,
        fn ($d) => getAhrefsMetrics($d, $config),
        fn ($d) => getMozMetrics($d, $config),
        $stripWww,
        $limit
    );

    if ($ext === 'csv') {
        writeCsv($output, $enriched, $delimiter ?? ',');
    } else {
        writeXlsx($output, $enriched);
    }

    logMessage('Finished. Output saved to ' . $output);
}

if (php_sapi_name() === 'cli') {
    try {
        main($argv);
    } catch (Throwable $e) {
        fwrite(STDERR, 'Error: ' . $e->getMessage() . PHP_EOL);
        exit(1);
    }
}

?>
