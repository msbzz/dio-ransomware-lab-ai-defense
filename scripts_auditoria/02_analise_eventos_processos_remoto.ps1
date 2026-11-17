# Etapa 02 - Inventario remoto SMB + WMI (somente leitura no Windows 7)
# Executar no Windows 11, em PowerShell interativo.
param(
 [string]$IP = '192.168.89.200',
 [string]$PastaLog = 'D:\temp\scripts_lab',
 [string]$Usuario = 'WIN-BTDHNBABNPN\investigador',
 [int]$MaxEventosPorLog = 30,
 [int]$HorasEventos = 48
)
$ErrorActionPreference = 'Continue'
$root = "\\$IP\RansomwareLab"
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$log = Join-Path $PastaLog "02_analise_eventos_processos_$stamp.txt"
$lines = New-Object 'System.Collections.Generic.List[string]'
function Add-Line([string]$s) { [void]$lines.Add($s); Write-Output $s }
function Report-Error([string]$area, $err) { Add-Line ("ERRO_{0}: {1}" -f $area, $err.Exception.Message) }
Add-Line "INICIO: $(Get-Date -Format s)"
Add-Line "ALVO_SMB: $root"
Add-Line "ALVO_WMI: $IP"
Add-Line 'MODO: somente leitura na VM; sem execucao remota de programas nem alteracoes.'

# 1. Inventario SMB original: as cinco pastas sao preservadas.
try {
 if (-not (Test-Path -LiteralPath $root -ErrorAction Stop)) { throw "Compartilhamento inacessivel: $root" }
 Add-Line 'SMB: acessivel'
 foreach ($folder in @('amostras','backup','evidencias','recuperados','simulador')) {
  $path = Join-Path $root $folder
  try {
   $items = @(Get-ChildItem -LiteralPath $path -Force -ErrorAction Stop)
   Add-Line "PASTA: $folder | itens=$($items.Count)"
   foreach ($f in $items) {
    Add-Line ("ITEM: {0} | tipo={1} | bytes={2} | alterado={3}" -f $f.FullName,$f.PSIsContainer,$f.Length,$f.LastWriteTime.ToString('s'))
   }
  } catch { Report-Error "PASTA_$folder" $_ }
 }
} catch { Report-Error 'ACESSO_SMB' $_ }

# 2. Uma credencial para todas as consultas WMI.
$cred = $null
try {
 Add-Line "CREDENCIAL_WMI: solicitando usuario $Usuario"
 $cred = Get-Credential -UserName $Usuario -Message 'Informe a senha do usuario do Windows 7 para consulta WMI'
 if ($null -eq $cred) { Add-Line 'WMI: credencial nao informada; consultas ignoradas.' }
} catch { Report-Error 'CREDENCIAL' $_ }

if ($null -ne $cred) {
 # 3. Verificacao inicial de conectividade/autorizacao WMI.
 $wmiOk = $false
 try {
  $os = Get-WmiObject -Class Win32_OperatingSystem -ComputerName $IP -Credential $cred -ErrorAction Stop
  Add-Line ("WMI: acessivel | SO={0} | versao={1}" -f $os.Caption,$os.Version)
  $wmiOk = $true
 } catch { Report-Error 'WMI_CONEXAO' $_ }

 if ($wmiOk) {
  # 4. Processos em execucao.
  try {
   Add-Line '=== PROCESSOS ==='
   $processos = @(Get-WmiObject -Class Win32_Process -ComputerName $IP -Credential $cred -ErrorAction Stop | Sort-Object Name,ProcessId)
   Add-Line "TOTAL_PROCESSOS: $($processos.Count)"
   foreach ($p in $processos) {
    Add-Line ("PROCESSO: nome={0} | pid={1} | executavel={2}" -f $p.Name,$p.ProcessId,$p.ExecutablePath)
   }
  } catch { Report-Error 'PROCESSOS' $_ }

  # 5. Servicos e estados.
  try {
   Add-Line '=== SERVICOS ==='
   $servicos = @(Get-WmiObject -Class Win32_Service -ComputerName $IP -Credential $cred -ErrorAction Stop | Sort-Object Name)
   Add-Line "TOTAL_SERVICOS: $($servicos.Count)"
   foreach ($s in $servicos) {
    Add-Line ("SERVICO: nome={0} | estado={1} | inicio={2} | conta={3}" -f $s.Name,$s.State,$s.StartMode,$s.StartName)
   }
  } catch { Report-Error 'SERVICOS' $_ }

  # 6. Eventos: consulta limitada por data e quantidade para evitar carga excessiva.
  $inicioWmi = (Get-Date).AddHours(-[Math]::Abs($HorasEventos)).ToUniversalTime().ToString('yyyyMMddHHmmss') + '.000000+000'
  foreach ($nomeLog in @('System','Application','Security')) {
   try {
    Add-Line "=== EVENTOS_$nomeLog (ultimas $HorasEventos horas; ate $MaxEventosPorLog) ==="
    $filter = "Logfile='$nomeLog' AND TimeGenerated >= '$inicioWmi'"
    $eventos = @(Get-WmiObject -Class Win32_NTLogEvent -ComputerName $IP -Credential $cred -Filter $filter -ErrorAction Stop |
      Sort-Object TimeGenerated -Descending | Select-Object -First $MaxEventosPorLog)
    Add-Line "EVENTOS_COLETADOS_$nomeLog`: $($eventos.Count)"
    foreach ($e in $eventos) {
     $msg = [string]$e.Message
     $msg = ($msg -replace '[\r\n]+',' ')
     if ($msg.Length -gt 300) { $msg = $msg.Substring(0,300) + '...' }
     Add-Line ("EVENTO: log={0} | id={1} | tipo={2} | origem={3} | dataWMI={4} | mensagem={5}" -f $nomeLog,$e.EventCode,$e.Type,$e.SourceName,$e.TimeGenerated,$msg)
    }
   } catch { Report-Error "EVENTOS_$nomeLog" $_ }
  }
 }
}
Add-Line "FIM: $(Get-Date -Format s)"
try {
 if (-not (Test-Path -LiteralPath $PastaLog)) { New-Item -ItemType Directory -Path $PastaLog -Force -ErrorAction Stop | Out-Null }
 $lines | Out-File -LiteralPath $log -Encoding UTF8 -ErrorAction Stop
 Write-Output "LOG_GERADO: $log"
} catch { Write-Output "ERRO_LOG: $($_.Exception.Message)" }
