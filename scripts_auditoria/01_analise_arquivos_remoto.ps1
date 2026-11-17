# DIO Ransomware Lab - Etapa 01: analise de arquivos (somente leitura na VM)
# Executar no Windows 11, pelo PicoClaw ou PowerShell 5.1.
# Unica escrita: log local no Windows 11, em D:\temp (deve existir).
[CmdletBinding()]
param(
    [string]$Raiz = '\\192.168.89.200\RansomwareLab',
    [string]$DiretorioLog = 'D:\temp'
)
$ErrorActionPreference = 'Stop'
$linhas = New-Object 'System.Collections.Generic.List[string]'
function Registrar([string]$Mensagem) {
    $linhas.Add($Mensagem)
    Write-Output $Mensagem
}
function HashArquivo([string]$Caminho) {
    return (Get-FileHash -LiteralPath $Caminho -Algorithm SHA256 -ErrorAction Stop).Hash
}
Registrar ('INICIO: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Registrar ('ORIGEM REMOTA: ' + $Raiz)
Registrar 'MODO: somente leitura no Windows 7; nenhum executavel remoto sera iniciado.'
try {
    if (-not (Test-Path -LiteralPath $Raiz -PathType Container)) {
        throw 'Compartilhamento inacessivel. Verifique a sessao SMB da conta investigador.'
    }
    $amostras = Join-Path $Raiz 'amostras'
    $backup = Join-Path $Raiz 'backup'
    $evidencias = Join-Path $Raiz 'evidencias'
    foreach ($p in @($amostras, $backup, $evidencias)) {
        if (-not (Test-Path -LiteralPath $p -PathType Container)) { throw ('Pasta nao encontrada/acessivel: ' + $p) }
    }
    $todos = @(Get-ChildItem -LiteralPath $Raiz -Recurse -File -ErrorAction Stop)
    Registrar ('TOTAL DE ARQUIVOS: ' + $todos.Count)
    foreach ($f in $todos) {
        $relativo = $f.FullName.Substring($Raiz.TrimEnd('\').Length).TrimStart('\')
        Registrar ('ARQUIVO | ' + $relativo + ' | bytes=' + $f.Length + ' | modificado=' + $f.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))
    }
    $suspeitos = @($todos | Where-Object { $_.Extension -match '^(?i:\.encrypted|\.locked|\.enc|\.crypt|\.ransom)$' })
    Registrar ('EXTENSOES SUSPEITAS ENCONTRADAS: ' + $suspeitos.Count)
    foreach ($f in $suspeitos) { Registrar ('SUSPEITO | ' + $f.FullName) }

    $arquivosAmostra = @(Get-ChildItem -LiteralPath $amostras -File -ErrorAction Stop)
    $arquivosBackup = @(Get-ChildItem -LiteralPath $backup -File -ErrorAction Stop)
    $nomes = @($arquivosAmostra.Name + $arquivosBackup.Name | Sort-Object -Unique)
    $iguais = 0; $diferentes = 0; $ausentes = 0
    foreach ($nome in $nomes) {
        $a = Join-Path $amostras $nome
        $b = Join-Path $backup $nome
        $temA = Test-Path -LiteralPath $a -PathType Leaf
        $temB = Test-Path -LiteralPath $b -PathType Leaf
        if (-not $temA -or -not $temB) {
            $ausentes++
            Registrar ('COMPARACAO | ' + $nome + ' | AUSENTE | amostras=' + $temA + ' | backup=' + $temB)
            continue
        }
        try {
            $ha = HashArquivo $a
            $hb = HashArquivo $b
            $estado = if ($ha -eq $hb) { $iguais++; 'IGUAL' } else { $diferentes++; 'DIFERENTE' }
            Registrar ('COMPARACAO | ' + $nome + ' | ' + $estado)
            Registrar ('  SHA256_AMOSTRA=' + $ha)
            Registrar ('  SHA256_BACKUP=' + $hb)
        } catch {
            Registrar ('ERRO_HASH | ' + $nome + ' | ' + $_.Exception.Message)
        }
    }
    Registrar ('RESUMO | iguais=' + $iguais + ' | diferentes=' + $diferentes + ' | ausentes=' + $ausentes)
    foreach ($nomeEvidencia in @('hashes_originais.txt','hashes_backup.txt','hashes_modificados.txt')) {
        $p = Join-Path $evidencias $nomeEvidencia
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            Registrar ('EVIDENCIA EXISTENTE | ' + $nomeEvidencia + ' | SHA256=' + (HashArquivo $p))
            Registrar ('INICIO_CONTEUDO_EVIDENCIA | ' + $nomeEvidencia)
            foreach ($linha in @(Get-Content -LiteralPath $p -ErrorAction Stop)) { Registrar ([string]$linha) }
            Registrar ('FIM_CONTEUDO_EVIDENCIA | ' + $nomeEvidencia)
        } else { Registrar ('EVIDENCIA AUSENTE | ' + $nomeEvidencia) }
    }
    Registrar 'CONCLUSAO: diferencas de hash nao comprovam, isoladamente, atividade de ransomware.'
} catch {
    Registrar ('ERRO GERAL: ' + $_.Exception.Message)
}
Registrar ('FIM: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
if (Test-Path -LiteralPath $DiretorioLog -PathType Container) {
    $destino = Join-Path $DiretorioLog ('01_analise_arquivos_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff') + '.txt')
    try {
        $linhas | Out-File -LiteralPath $destino -Encoding UTF8 -ErrorAction Stop
        Write-Output ('LOG LOCAL: ' + $destino)
    } catch { Write-Output ('AVISO: falha ao gravar log local: ' + $_.Exception.Message) }
} else {
    Write-Output ('AVISO: pasta local de logs nao existe: ' + $DiretorioLog)
}
