# Windows 7 PowerShell 2.0 - somente leitura dos dados do laboratorio
$base = 'C:\RansomwareLab'
$logDir = Join-Path $base 'logs_auditoria\01_analise_arquivos'
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$log = Join-Path $logDir ("01_analise_arquivos_{0}.txt" -f (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
function Write-Log($msg) { $msg | Out-File -FilePath $log -Append -Encoding UTF8 }
Write-Log ("INICIO: " + (Get-Date))
Write-Log ("MAQUINA: " + $env:COMPUTERNAME)
foreach ($folder in @('amostras','backup','evidencias','recuperados','simulador')) {
  $path = Join-Path $base $folder
  Write-Log ("`r`n=== PASTA: " + $path + " ===")
  if (!(Test-Path $path)) { Write-Log "ERRO: pasta inexistente"; continue }
  try {
    $files = @(Get-ChildItem -Path $path -Recurse -Force -ErrorAction Stop | Where-Object { !$_.PSIsContainer })
    Write-Log ("TOTAL_ARQUIVOS: " + $files.Count)
    foreach ($f in $files) {
      try {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $stream = [System.IO.File]::OpenRead($f.FullName)
        try { $hash = [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','') }
        finally { $stream.Close(); $sha.Clear() }
        Write-Log ("ARQUIVO | {0} | bytes={1} | alterado={2} | SHA256={3}" -f $f.FullName,$f.Length,$f.LastWriteTime,$hash)
      } catch { Write-Log ("ERRO_HASH | {0} | {1}" -f $f.FullName,$_.Exception.Message) }
    }
  } catch { Write-Log ("ERRO_LISTAGEM: " + $_.Exception.Message) }
}
Write-Log ("`r`nFIM: " + (Get-Date))
Write-Host "LOG: $log"
