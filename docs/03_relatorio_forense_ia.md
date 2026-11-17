# Investigação de Segurança e Resposta a Incidentes com Agente de IA (PicoClaw)

Este documento reúne os prompts operacionais enviados ao agente de IA (**PicoClaw** rodando no host Windows 11) e o **Relatório Técnico Forense** real produzido pela leitura remota dos logs e artefatos da VM Windows 7 via SMB.

---

## Parte 1 — Prompt de Investigação Forense (Etapa 03)

```markdown
Realize uma investigação de segurança na VM Windows 7, IP `192.168.89.200`, utilizando PowerShell real.

1. Autenticação SMB
- Servidor: `192.168.89.200`
- Usuário: `WIN-BTDHNBABNPN\investigador`
- Compartilhamento: `\\192.168.89.200\RansomwareLab`
- Reutilize inicialmente a sessão SMB existente, sem solicitar usuário ou senha. Não coloque senhas em comandos ou arquivos de log.

2. Leitura dos relatórios
Acesse `\\192.168.89.200\RansomwareLab\logs_auditoria` e leia os relatórios mais recentes:
- `01_analise_arquivos`
- `02_analise_eventos_processos`

3. Investigação de segurança
Analise os relatórios procurando:
- Arquivos modificados, excluídos ou suspeitos.
- Processos desconhecidos e seus caminhos.
- Serviços com nomes incomuns (investigue especialmente o serviço `mizAERSkP`, associado ao executável `KcPcJp.exe` em `%TEMP%`).
- Eventos relevantes de segurança e indicadores de possível comprometimento.

4. Diagnóstico
Apresente:
1. Evidências efetivamente encontradas.
2. Indicadores suspeitos e sua justificativa.
3. Possíveis relações com a simulação de ransomware.
4. Classificação dos achados: confirmado, suspeito ou inconclusivo.
5. Recomendações de defesa e recuperação.
6. Limitações da investigação.

5. Restrições
- Investigação exclusivamente de leitura. Não modificar, excluir ou executar arquivos da VM.
```

---

## Parte 2 — Relatório Técnico Produzido pelo PicoClaw

> **Alvo:** `192.168.89.200` — `WIN-BTDHNBABNPN`  
> **Data da coleta:** 16/11/2026  
> **Método:** PowerShell 5.1 real no Windows 11, com leitura de arquivos e evidências via SMB (`\\192.168.89.200\RansomwareLab`).

### 1. Resumo Executivo

A investigação identificou:
- **Alterações confirmadas em dois arquivos de teste:** `clientes.txt` e `financeiro.txt`, com diferenças de conteúdo, tamanho e hash SHA-256 em relação ao backup. Os conteúdos continuam legíveis e apresentam acréscimos textuais; não demonstram criptografia ativa por ransomware no momento da coleta.
- **Um serviço de alta suspeição:** `mizAERSkP` (nome de exibição `MDqUlLY`), configurado para inicialização automática (`Auto`) e associado ao caminho `C:\Users\marco\AppData\Local\Temp\KcPcJp.exe`.
- O serviço aparece parado (`Stopped`) em dois relatórios, mas isso não comprova que nunca tenha sido executado.
- **Logons de rede registrados** a partir de `192.168.89.1` (estação `DESKTOP-LTRDV8B`), compatíveis com as consultas originadas no host.
- Nenhuma evidência suficiente nos logs recortados para confirmar ransomware ativo ou atribuir as alterações textuais ao serviço suspeito.

Nenhum arquivo suspeito foi executado, nenhum arquivo da VM foi modificado e nenhuma configuração foi alterada.

### 2. Fontes e Evidências Auditadas

Todos os caminhos abaixo foram lidos a partir de `\\192.168.89.200\RansomwareLab\`:

- **`[R1]` Análise de arquivos:** `logs_auditoria\01_analise_arquivos\01_analise_arquivos_20261116_165628_361.txt`
  - Tamanho: 2.624 bytes | SHA-256: `E6AD8AF04547737359B9F877A3755E0E5C7AA9986966CCB1E2859290775500CD`
- **`[R2]` Eventos e processos (mais recente):** `logs_auditoria\02_analise_eventos_processos\02_analise_eventos_processos_20261116_200053_017.txt`
  - Tamanho: 109.082 bytes | SHA-256: `6044F0057C319080CE4641B65C58B9A160CD6F9B42CA5EFC89683240DC6C80DF`
- **`[R3]` Eventos e processos (anterior):** `logs_auditoria\02_analise_eventos_processos\02_analise_eventos_processos_20261116_165102_845.txt`
  - SHA-256: `F5A607A0BE46E01405E7149C9678A1F88848E465DE86658BB058B6C08E946317`
- **Fontes complementares verificadas:** `evidencias\hashes_originais.txt`, `evidencias\hashes_backup.txt`, `evidencias\hashes_modificados.txt` e arquivos das pastas `amostras` e `backup`.

### 3. Análise de Integridade dos Arquivos (SHA-256)

| Arquivo | Tamanho no Backup | Tamanho na Amostra | Comparação SHA-256 |
|---|---:|---:|---|
| `clientes.txt` | 32 bytes | 72 bytes | **SHA-256 diferente** |
| `financeiro.txt` | 37 bytes | 80 bytes | **SHA-256 diferente** |
| `confidencial.txt` | 34 bytes | 34 bytes | SHA-256 igual |
| `contrato.txt` | 35 bytes | 35 bytes | SHA-256 igual |
| `interno.txt` | 33 bytes | 33 bytes | SHA-256 igual |

- **Conteúdo adicional em `amostras\clientes.txt`:** `Novo cliente cadastrado em 12-11-2026`
- **Conteúdo adicional em `amostras\financeiro.txt`:** `Receita adicional de R$ 15000 registrada`
- Os hashes de `hashes_originais.txt` coincidem integralmente com a pasta `backup`; os de `hashes_modificados.txt` coincidem com as amostras atuais.

### 4. Análise do Serviço Suspeito (`mizAERSkP` / `KcPcJp.exe`)

Os relatórios `[R2]` e `[R3]` registram a seguinte entrada em `Win32_Service`:

```text
Name        : mizAERSkP
DisplayName : MDqUlLY
State       : Stopped
StartMode   : Auto
PathName    : C:\Users\marco\AppData\Local\Temp\KcPcJp.exe
```

**Justificativas técnicas da suspeição:**
1. Nome de serviço, nome de exibição e nome de executável com padrão aleatório, sem identificação funcional ou fornecedor legítimo.
2. Binário apontando para pasta temporária de perfil de usuário (`AppData\Local\Temp`), local atípico para serviços legítimos do sistema e recorrente em artefatos de pós-exploração/malware.
3. Modo de inicialização `Auto`, compatível com mecanismo de persistência.

### 5. Processos, Eventos de Segurança e Volume Shadow Copy (VSS)

- **Processos (`Win32_Process`):** Caminhos compatíveis com processos nativos do Windows, VMware Tools e a execução do próprio script de auditoria via Agendador de Tarefas (`powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\RansomwareLab\scripts_auditoria\02_analise_eventos_processos_local.ps1`).
- **Eventos Security:** 15 eventos `4624` (logon de rede tipo 3) e 15 eventos `4634` (logoff) originados de `192.168.89.1` (`DESKTOP-LTRDV8B`).
- **Serviço VSS (Cópias de Sombra):** O evento Application `8224` registra encerramento normal por ociosidade (*The VSS service is shutting down due to idle timeout*), **não** configurando exclusão maliciosa de *shadow copies* (`vssadmin delete shadows`).

### 6. Classificação Consolidada dos Achados

| Achado | Classificação |
|---|---|
| Diferenças de tamanho e hash em `clientes.txt` e `financeiro.txt` | **Confirmado** |
| Integridade preservada nos backups e nos outros 3 arquivos | **Confirmado** |
| Serviço `mizAERSkP` automático apontando para `%TEMP%\KcPcJp.exe` | **Suspeito — Alta Prioridade** |
| Envolvimento do serviço nas alterações dos arquivos de teste | **Inconclusivo** |
| Exclusão de arquivos ou sabotagem de *Shadow Copies* (VSS) | **Não demonstrada** |

---

## Parte 3 — Prompt de Validação de Recuperação (Etapa 04)

Para concluir o ciclo de resposta a incidentes sem ações destrutivas não autorizadas, foi elaborado o prompt da **Etapa 04** para validação pré-restauração e gravação automatizada de parecer em `logs_auditoria\log_agent_ia`:

```markdown
# ETAPA 04 — Validação de recuperação dos arquivos

Realize a Etapa 04 do laboratório de segurança na VM Windows 7, IP `192.168.89.200`, utilizando PowerShell real no Windows 11.

1. Utilize os caminhos:
- `\\192.168.89.200\RansomwareLab\amostras`
- `\\192.168.89.200\RansomwareLab\backup`
- `\\192.168.89.200\RansomwareLab\evidencias`

2. Execute somente as verificações necessárias (somente leitura nas pastas de dados):
- Confirme a existência dos cinco backups.
- Recalcule o SHA-256 dos backups e compare com `hashes_originais.txt`.
- Confirme quais arquivos atuais diferem dos backups.
- Determine quais arquivos poderiam ser restaurados com segurança e apresente o plano de restauração.
- Informe quais alterações pós-backup (Estado V2) seriam perdidas caso a restauração ocorra a partir do backup V1 em vez da descriptografia.
```
