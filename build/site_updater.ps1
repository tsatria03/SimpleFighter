param([string]$HtmlFile, [string]$Version, [string]$Tag)
$c = (Get-Content $HtmlFile) -replace '(SimpleFighter V)\d+\.\d+', "`${1}$Version" -replace '(releases/(?:download|tag)/)V\d+\.\d+', "`${1}$Tag"
[System.IO.File]::WriteAllLines($HtmlFile, $c)
