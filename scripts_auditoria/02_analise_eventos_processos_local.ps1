# Windows 7 PowerShell 2.0 - coleta local, somente leitura
$base = 'C:\RansomwareLab'
$logDir = Join-Path $base 'logs_auditoria\02_analise_eventos_processos'
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$log = Join-Path $logDir ("02_analise_eventos_processos_{0}.txt" -f (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
function Write-Log($msg) { $msg | Out-File -FilePath $log -Append -Encoding UTF8 }
function Section($name, $block) {
  Write-Log ("`r`n=== " + $name + " ===")
  try { $result = & $block; if ($null -eq $result) { Write-Log 'SEM RESULTADOS' } else { $result | Out-String -Width 240 | Out-File -FilePath $log -Append -Encoding UTF8 } }
  catch { Write-Log ("ERRO: " + $_.Exception.Message) }
}
Write-Log ("INICIO: " + (Get-Date))
Write-Log ("MAQUINA: " + $env:COMPUTERNAME)
Section 'SISTEMA OPERACIONAL' { Get-WmiObject Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,LastBootUpTime }
Section 'PROCESSOS' { Get-WmiObject Win32_Process | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine }
Section 'SERVICOS' { Get-WmiObject Win32_Service | Select-Object Name,DisplayName,State,StartMode,PathName }
$start = (Get-Date).AddHours(-48)
foreach ($name in @('System','Application','Security')) {
  Write-Log ("`r`n=== EVENTOS " + $name + " (48h, max 30) ===")
  try {
    $events = @(Get-EventLog -LogName $name -After $start -Newest 30 -ErrorAction Stop)
    Write-Log ("EVENTOS_COLETADOS: " + $events.Count)
    if ($events.Count -gt 0) {
      $events | Select-Object TimeGenerated,EntryType,EventID,Source,Message | Out-String -Width 240 | Out-File -FilePath $log -Append -Encoding UTF8
    }
  } catch { Write-Log ("ERRO_EVENTOS_" + $name + ": " + $_.Exception.Message) }
}
Write-Log ("`r`nFIM: " + (Get-Date))
Write-Host "LOG: $log"
