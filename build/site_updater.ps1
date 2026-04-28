param([string]$HtmlFile, [string]$Version, [string]$Tag)
$c = (Get-Content $HtmlFile) -replace 'V[\d]+\.[\d]+0', $Tag -replace 'V[\d]+\.[\d]+(?<!0)', "V$Version"
[System.IO.File]::WriteAllLines($HtmlFile, $c)
