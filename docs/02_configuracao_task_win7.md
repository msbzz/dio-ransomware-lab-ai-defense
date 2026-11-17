# Tutorial — Configurar Tarefas Agendadas de Auditoria no Windows 7 Home

**Objetivo:** Executar localmente scripts PowerShell 2.0 de auditoria dentro da máquina virtual Windows 7, gerando logs individuais com carimbo de data/hora que posteriormente são lidos via SMB pelo agente **PicoClaw** instalado no Windows 11.

Essa arquitetura resolve limitações de consulta remota de serviços/eventos via DCOM/WMI e garante que o agente de IA no host trabalhe em modo **100% leitura** sobre evidências consolidadas.

---

## 1. Preparação do Ambiente na VM Windows 7

| Item | Configuração |
|---|---|
| **Sistema operacional** | Windows 7 Home Basic |
| **Usuário de execução** | `WIN-BTDHNBABNPN\investigador` |
| **Pasta dos scripts na VM** | `C:\RansomwareLab\scripts_auditoria` |
| **Tarefa 01 (Arquivos e Hashes)** | `Auditoria_01_Arquivos` → `01_analise_arquivos_local.ps1` |
| **Tarefa 02 (Processos, Serviços e Eventos)** | `Auditoria_02_Eventos_Processos` → `02_analise_eventos_processos_local.ps1` |
| **Pasta de saída dos relatórios** | `C:\RansomwareLab\logs_auditoria\` |

---

## 2. Abrir o Agendador de Tarefas (`taskschd.msc`)

1. No Windows 7, clique em **Iniciar**, digite `taskschd.msc` e pressione **Enter**.
2. No menu superior ou painel direito, selecione **Action → Create Task...** (utiliza-se *Create Task* em vez de *Create Basic Task* para configurar privilégios e execução independente de sessão interativa).

---

## 3. Configurar a Aba General

Preencha os campos conforme abaixo:

| Campo | Valor |
|---|---|
| **Name** | `Auditoria_01_Arquivos` (e `Auditoria_02_Eventos_Processos` para a segunda tarefa) |
| **Description** | `Auditoria local com geracao de logs independentes para analise por IA` |
| **User account** | `WIN-BTDHNBABNPN\investigador` |
| **Run whether user is logged on or not** | Selecionado |
| **Do not store password** | Marcado |
| **Run with highest privileges** | Marcado |
| **Configure for** | Windows 7, Windows Server 2008 R2 (ou Windows Vista, Windows Server 2008) |

![Configuração Task Scheduler 01](../imgs/config%20taskmanager%20win7_01.png)

---

## 4. Configurar a Aba Triggers

1. Clique em **Triggers → New...**.
2. Configure:
   - **Begin the task:** `On a schedule`
   - **Settings:** `One time` (ou periódico conforme a janela de monitoramento)
   - **Enabled:** Marcado
3. Clique em **OK**.

---

## 5. Configurar a Aba Actions

1. Clique em **Actions → New...** e selecione `Start a program`.
2. Preencha os três campos:

**Program/script:**
```text
powershell.exe
```

**Add arguments (optional) — Para a Tarefa 01:**
```text
-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\RansomwareLab\scripts_auditoria\01_analise_arquivos_local.ps1"
```

**Add arguments (optional) — Para a Tarefa 02:**
```text
-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\RansomwareLab\scripts_auditoria\02_analise_eventos_processos_local.ps1"
```

**Start in (optional):**
```text
C:\RansomwareLab\scripts_auditoria
```

![Configuração Task Scheduler 02](../imgs/config%20taskmanager%20win7_02.png)

> **Nota técnica:** O parâmetro `-ExecutionPolicy Bypass` aplica-se apenas ao processo iniciado pela tarefa, sem enfraquecer a política global do PowerShell na máquina.

---

## 6. Configurar as Abas Conditions e Settings

Na aba **Conditions**, desmarque as restrições de ociosidade e energia (*Start the task only if the computer is idle / on AC power*) para garantir a execução imediata no laboratório.

Na aba **Settings**, mantenha:
- `Allow task to be run on demand`: **Marcado**
- `Run task as soon as possible after a scheduled start is missed`: **Marcado**
- `Stop the task if it runs longer than`: **1 hour**
- `If the task is already running`: `Do not start a new instance`

![Configuração Task Scheduler 03](../imgs/config%20taskmanager%20win7_03.png)

---

## 7. Execução e Verificação dos Logs Gerados

No painel **Task Scheduler Library**, as duas tarefas agendadas ficam disponíveis para execução automática ou sob demanda (**Run**):

![Tarefas de Monitoramento Agendadas](../imgs/tarefas%20de%20monitoramento%20agendadas.png)

A cada execução, os scripts geram arquivos únicos em `C:\RansomwareLab\logs_auditoria\` sem sobrescrever evidências anteriores:

- `logs_auditoria\01_analise_arquivos\01_analise_arquivos_AAAAMMDD_HHMMSS_fff.txt`
- `logs_auditoria\02_analise_eventos_processos\02_analise_eventos_processos_AAAAMMDD_HHMMSS_fff.txt`

> **Compatibilidade com PowerShell 2.0 (Windows 7):** Como o PowerShell 2.0 nativo do Windows 7 não possui o cmdlet `Get-FileHash` (introduzido no PowerShell 4.0), o script [`01_analise_arquivos_local.ps1`](../scripts_auditoria/01_analise_arquivos_local.ps1) implementa o cálculo SHA-256 diretamente via classe `.NET` `[System.Security.Cryptography.SHA256]::Create()`.
