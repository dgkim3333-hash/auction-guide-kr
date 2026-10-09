# 경매 분석 MCP 키 입력 도우미 (auction-guide-kr 05단원)
# 하는 일: 설정 파일의 <<여기에_...>> 자리를 찾아, 화면에 보이지 않게 키를 입력받아 채웁니다.
#  - 설정 파일 내용과 키는 화면에 출력하지 않습니다
#  - 고치기 전에 같은 폴더에 백업(.bak_날짜시각)을 만듭니다
#  - 같은 자리표시(예: 공공데이터포털 키 3곳)는 한 번만 묻고 전부 채웁니다
#  - 저장 전에 JSON 형식을 검사하고, 틀리면 저장하지 않습니다

$ErrorActionPreference = 'Stop'

# 1) Claude 가 켜져 있으면 중단 (켜진 채 고치면 덮어써질 수 있음)
if (Get-Process -Name 'claude' -ErrorAction SilentlyContinue) {
    Write-Host '[중단] Claude 가 실행 중입니다. 작업 표시줄 트레이까지 완전히 종료한 뒤 다시 실행하세요.' -ForegroundColor Red
    exit 1
}

# 2) 설정 파일 찾기 (일반 설치판 · Microsoft Store 판)
$cands = @()
$p1 = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
if (Test-Path $p1) { $cands += $p1 }
$store = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA 'Packages') -Directory -Filter 'Claude_*' -ErrorAction SilentlyContinue
foreach ($d in $store) {
    $p2 = Join-Path $d.FullName 'LocalCache\Roaming\Claude\claude_desktop_config.json'
    if (Test-Path $p2) { $cands += $p2 }
}
if ($cands.Count -eq 0) {
    Write-Host '[중단] 설정 파일을 찾지 못했습니다. Claude 앱 → 설정 → 개발자 → 설정 편집 을 한 번 눌러 파일을 만든 뒤 다시 실행하세요.' -ForegroundColor Red
    exit 1
}
$cfg = $cands[0]
if ($cands.Count -gt 1) {
    Write-Host '설정 파일이 여러 개 있습니다. 번호를 고르세요.'
    for ($i = 0; $i -lt $cands.Count; $i++) { Write-Host ("  [{0}] {1}" -f ($i + 1), $cands[$i]) }
    $n = Read-Host '번호'
    $cfg = $cands[[int]$n - 1]
}
Write-Host ("대상 파일: {0}" -f $cfg)

# 3) 백업
$bak = $cfg + '.bak_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
Copy-Item -Path $cfg -Destination $bak
Write-Host ("백업: {0}" -f $bak) -ForegroundColor Green

# 4) 자리표시 찾기
$text = [IO.File]::ReadAllText($cfg, [Text.Encoding]::UTF8)
$found = [regex]::Matches($text, '<<([^<>]+)>>') | ForEach-Object { $_.Value } | Select-Object -Unique
if (-not $found) {
    Write-Host '채울 자리(<<여기에_...>>)가 없습니다. 05단원의 설정 블록을 먼저 붙여넣었는지 확인하세요.' -ForegroundColor Yellow
    exit 0
}

# 5) 키 입력 (화면에 보이지 않음). 빈칸으로 Enter 를 누르면 건너뜀
$filled = @(); $skipped = @()
foreach ($ph in $found) {
    $label = $ph.Trim('<', '>')
    $sec = Read-Host -AsSecureString ("{0}  (붙여넣고 Enter · 건너뛰려면 그냥 Enter)" -f $label)
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { $val = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
    $val = ($val -replace '\s', '')
    # 같은 키를 두 번 붙여넣어 길이가 두 배가 된 경우 한 번으로 줄임
    if ($val.Length -ge 2 -and $val.Length % 2 -eq 0) {
        $h = $val.Length / 2
        if ($val.Substring(0, $h) -eq $val.Substring($h)) { $val = $val.Substring(0, $h) }
    }
    if ([string]::IsNullOrEmpty($val)) { $skipped += $label; continue }
    $safe = $val.Replace('\', '\\').Replace('"', '\"')
    $text = $text.Replace($ph, $safe)
    $filled += $label
    $val = $null; $safe = $null
}

# 6) JSON 검사 — 틀리면 저장하지 않음 (내용은 출력하지 않음)
try { $null = $text | ConvertFrom-Json }
catch {
    Write-Host '[중단] JSON 형식 오류가 있어 저장하지 않았습니다. 콤마·따옴표를 확인하세요. 원본은 그대로입니다.' -ForegroundColor Red
    exit 1
}

# 7) 저장 (UTF-8, BOM 없음)
[IO.File]::WriteAllText($cfg, $text, (New-Object Text.UTF8Encoding($false)))

Write-Host ''
Write-Host ("채움 {0}개: {1}" -f $filled.Count, ($filled -join ' / ')) -ForegroundColor Green
if ($skipped.Count) { Write-Host ("건너뜀 {0}개: {1}" -f $skipped.Count, ($skipped -join ' / ')) -ForegroundColor Yellow }
Write-Host '끝났습니다. Claude 를 다시 켜고 새 작업에서 연결을 확인하세요.'
