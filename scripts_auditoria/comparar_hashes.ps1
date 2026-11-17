$origem = "testes\RansomwareLab\amostras"
$backup = "testes\RansomwareLab\backup"

Get-ChildItem "$origem\*.txt" | ForEach-Object {
    $nome = $_.Name
    $hashOriginal = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    $hashBackup = (Get-FileHash "$backup\$nome" -Algorithm SHA256).Hash

    if ($hashOriginal -eq $hashBackup) {
        Write-Host "[OK] $nome - Hashes identicos" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] $nome - Hashes diferentes" -ForegroundColor Red
    }
}