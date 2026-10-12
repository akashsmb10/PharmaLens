$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
$deckPath = Join-Path $projectPath 'deliverables\Phase7_Axtria_Project_Presentation.pptx'
$renderPath = Join-Path $projectPath 'docs\assets\slides'
$statusPath = Join-Path $projectPath 'outputs\phase7\validation\native_presentation_render.json'
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) {
    throw 'A PowerPoint session already exists; automatic rendering will not disturb it.'
}
New-Item -ItemType Directory -Path $renderPath -Force | Out-Null
$powerPoint = $null
$presentation = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerPoint.Presentations.Open($deckPath, -1, 0, 0)
    $presentation.Export($renderPath, 'PNG', 1440, 810)
    $presentation.SaveAs((Join-Path $projectPath 'deliverables\Phase7_Axtria_Project_Presentation.pdf'), 32)
    $result = @{ rendered = $true; renderer = 'Installed Microsoft PowerPoint'; slides = $presentation.Slides.Count; images = @(Get-ChildItem -LiteralPath $renderPath -Filter '*.PNG').Count; pdf = $true; visually_reviewed = $false }
    $result | ConvertTo-Json | Set-Content -LiteralPath $statusPath -Encoding UTF8
    Write-Output 'Native PowerPoint slide images and PDF exported.'
} finally {
    if ($null -ne $presentation) { $presentation.Close(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null }
    if ($null -ne $powerPoint) { $powerPoint.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint) | Out-Null }
}
