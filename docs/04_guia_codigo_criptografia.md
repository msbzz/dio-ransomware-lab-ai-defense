# Criptografia comentada — guia para iniciantes em Python

**Arquivo estudado:** `criptografar_beta(1).py`  
**Objetivo:** entender o que o programa faz, como suas funções se relacionam e por que cada parâmetro é usado.

> **Importante:** este programa cria **cópias criptografadas** dos cinco arquivos de amostra. Ele **não criptografa nem apaga os originais**. Também tenta criar backups antes de criptografar. Use somente arquivos de teste.

## 1. Visão geral: qual problema o código resolve?

O script simula uma etapa de criptografia em um laboratório controlado. Ele identifica o ambiente pela localização do arquivo `.py` ou `.exe`, verifica a estrutura das pastas, confirma a presença de cinco amostras, solicita autorização, cria backups quando ainda não existem, gera uma chave Fernet e grava cópias criptografadas com a extensão `.encrypted`.

**Sequência de execução:**

1. O Python executa o bloco `if __name__ == '__main__'`.
2. Esse bloco chama `main()`.
3. `main()` chama `localizar()` para descobrir o diretório-base e o modo.
4. `main()` verifica as pastas, os arquivos e a inexistência de saídas e chave anteriores.
5. O usuário confirma digitando `SIMULAR`.
6. O programa cria backups ausentes, grava uma nova chave e criptografa cópias.
7. Se ocorrer uma exceção, o bloco `except` exibe a mensagem e encerra com código de erro.

**Limite importante:** o valor `modo` é apenas exibido. Não existe, neste código, uma regra de criptografia diferente para `laboratorio` e `desenvolvimento`.

## 2. Código original, com formatação preservada

```python
# -*- coding: utf-8 -*-
"""Laboratório didático: criptografa cópias de cinco amostras, preservando originais."""
from pathlib import Path
import sys
import shutil
import hashlib
from cryptography.fernet import Fernet

NOMES = ('clientes.txt', 'confidencial.txt', 'contrato.txt', 'financeiro.txt', 'interno.txt')


def localizar():
    # No executável, sys.executable indica onde o .exe está instalado.
    # No Python, __file__ indica onde o próprio .py está salvo.
    pasta = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
    if pasta.name.lower() != 'simulador':
        raise RuntimeError('Execute a partir de uma pasta chamada simulador.')
    if pasta.parent.name.lower() == 'ransomwarelab':
        return pasta.parent, 'laboratorio'
    if pasta.parent.name.lower() == 'lab-ransomware':
        return pasta.parent / 'testes' / 'RansomwareLab', 'desenvolvimento'
    raise RuntimeError('Caminho não reconhecido; operação cancelada.')


def main():
    lab, modo = localizar()
    amostras, backup = lab / 'amostras', lab / 'backup'
    simulador = lab / 'simulador'
    if not amostras.is_dir() or not backup.is_dir() or not simulador.is_dir():
        raise RuntimeError('Estrutura do laboratório incompleta.')
    arquivos = [amostras / nome for nome in NOMES]
    saidas = [amostras / (nome + '.encrypted') for nome in NOMES]
    chave = simulador / 'chave_recuperacao.key'
    # Validação prévia evita sobrescrever resultados de outro teste.
    for arq, saida in zip(arquivos, saidas):
        if arq.is_symlink() or not arq.is_file() or saida.exists() or saida.is_symlink():
            raise RuntimeError('Amostra ausente ou resultado existente: ' + arq.name)
    if chave.exists() or chave.is_symlink():
        raise RuntimeError('Já existe chave de recuperação. Preserve a chave anterior.')
    print('Modo detectado:', modo)
    print('Serão criadas cópias criptografadas; originais serão preservados.')
    if input('Digite SIMULAR para continuar: ') != 'SIMULAR':
        print('Cancelado.')
        return
    # Guardamos uma cópia de segurança sem substituir backups existentes.
    for arq in arquivos:
        destino = backup / arq.name
        if destino.is_symlink():
            raise RuntimeError('Backup inválido: ' + destino.name)
        if not destino.exists():
            shutil.copy2(str(arq), str(destino))
    token = Fernet.generate_key()
    with chave.open('xb') as f:
        f.write(token)
    cifrador = Fernet(token)
    for arq, saida in zip(arquivos, saidas):
        with saida.open('xb') as f:
            f.write(cifrador.encrypt(arq.read_bytes()))
        print('[CRIPTOGRAFADO EM CÓPIA]', arq.name)
    print('Concluído. Originais e backups preservados.')


if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
```

## 3. Bibliotecas e dados iniciais

### `from pathlib import Path`

`Path` representa um caminho de arquivo ou diretório. Em vez de concatenar barras manualmente, o programa usa `lab / 'amostras'`. **Parâmetro do construtor `Path(...)`:** um caminho, por exemplo `Path('C:/RansomwareLab')`. O operador `/` une partes do caminho; aqui **não significa divisão matemática**.

### `import sys`

Dá acesso a informações sobre o processo Python. Neste script, `sys.executable` ajuda a localizar o programa empacotado e `sys.exit(1)` sinaliza término com erro.

### `import shutil`

Disponibiliza operações de arquivos. O script usa `shutil.copy2(origem, destino)` para copiar os arquivos de amostra e preservar metadados quando possível.

### `import hashlib`

Biblioteca para cálculo de hashes. **Foi importada, mas não é utilizada neste arquivo**. O programa não calcula hashes nesta etapa.

### `from cryptography.fernet import Fernet`

Importa `Fernet`, classe de criptografia simétrica autenticada. A chave gerada serve tanto para criptografar quanto para recuperar os dados. Ela precisa ser protegida.

### `NOMES = (...)`

`NOMES` é uma **tupla** com os cinco nomes de arquivo. A tupla é uma sequência ordenada; seus elementos não podem ser substituídos diretamente. `NOMES[0]` retorna `clientes.txt` porque a contagem de índices começa em zero.

## 4. Função `localizar()` — identificar o ambiente

### Objetivo e retorno

**Por que existe?** Para impedir que o programa use um diretório-base arbitrário. Ela identifica onde está o próprio script ou executável e verifica os nomes esperados das pastas.

**Assinatura:** `def localizar():`  
**Parâmetros:** nenhum. Os parênteses vazios significam que a função não recebe argumentos.  
**Retorno:** dois valores, `(caminho_base, modo)`, quando o caminho corresponde a um dos padrões aceitos. Caso contrário, lança `RuntimeError`.

### Explicação linha a linha

```python
pasta = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
```

Essa expressão reúne várias operações:

1. `getattr(sys, 'frozen', False)` consulta o atributo `frozen` do módulo `sys`. Seus argumentos são: **objeto** (`sys`), **nome do atributo** (`'frozen'`) e **valor padrão** (`False`) caso não exista. Ferramentas de empacotamento, como PyInstaller, podem definir esse atributo.
2. `A if condição else B` é uma expressão condicional: escolhe `sys.executable` se `frozen` for verdadeiro; caso contrário, escolhe `__file__`.
3. `sys.executable` fornece o caminho do executável em execução; quando o script não está empacotado, `__file__` identifica o arquivo `.py`.
4. `Path(...)` transforma o caminho em objeto `Path`.
5. `.resolve()` produz um caminho absoluto e resolve referências de caminho.
6. `.parent` devolve a pasta que contém o arquivo.

**Exemplo:** se o script estiver em `C:\RansomwareLab\simulador\criptografar_beta.py`, a variável `pasta` representa `C:\RansomwareLab\simulador`.

```python
if pasta.name.lower() != 'simulador':
    raise RuntimeError('Execute a partir de uma pasta chamada simulador.')
```

- `pasta.name` extrai apenas o nome da pasta final.
- `.lower()` converte o nome para minúsculas, permitindo comparar `Simulador` com `simulador`.
- `!=` significa **diferente de**.
- `if` executa o bloco quando a condição é verdadeira.
- `raise RuntimeError(mensagem)` interrompe o fluxo normal, lançando uma exceção com a mensagem indicada.

```python
if pasta.parent.name.lower() == 'ransomwarelab':
    return pasta.parent, 'laboratorio'
```

Aqui, `pasta.parent` é a pasta **acima** de `simulador`. `==` verifica igualdade. Se ela se chamar `RansomwareLab` (ignorando maiúsculas), `return` devolve o diretório superior e a etiqueta `laboratorio`. **`return` também encerra a execução da função.**

```python
if pasta.parent.name.lower() == 'lab-ransomware':
    return pasta.parent / 'testes' / 'RansomwareLab', 'desenvolvimento'
```

Se a pasta acima de `simulador` se chamar `lab-ransomware`, a função monta o caminho `lab-ransomware/testes/RansomwareLab` e devolve a etiqueta `desenvolvimento`. Isso não muda o algoritmo de criptografia; apenas muda o diretório-base escolhido.

```python
raise RuntimeError('Caminho não reconhecido; operação cancelada.')
```

Esse último `raise` é alcançado quando nenhuma condição anterior retornou um resultado. **A função valida nomes de pastas, mas não prova que o caminho pertence a uma instalação confiável.**

## 5. Função `main()` — coordenar a operação

### Objetivo e parâmetros

`main()` organiza todas as etapas: localização, validação, confirmação, backup, geração de chave e criação de cópias criptografadas.

**Assinatura:** `def main():`  
**Parâmetros:** nenhum.  
**Retorno:** normalmente não retorna um valor explícito (`None`). Pode terminar antecipadamente com `return` quando o usuário cancela ou lançar exceções em caso de falha.

### 5.1. Receber o ambiente e montar os caminhos

```python
lab, modo = localizar()
amostras, backup = lab / 'amostras', lab / 'backup'
simulador = lab / 'simulador'
```

A primeira linha chama `localizar()` e **desempacota** seus dois retornos em `lab` e `modo`. As outras duas constroem caminhos para as três pastas de trabalho. Nenhuma pasta é criada aqui: o código apenas representa seus caminhos.

### 5.2. Conferir a estrutura

```python
if not amostras.is_dir() or not backup.is_dir() or not simulador.is_dir():
    raise RuntimeError('Estrutura do laboratório incompleta.')
```

`is_dir()` retorna `True` quando o caminho representa um diretório. `not` inverte o valor lógico. `or` significa que **basta uma das três verificações falhar** para o programa lançar o erro. O método não recebe parâmetros.

### 5.3. Montar listas de entrada e saída

```python
arquivos = [amostras / nome for nome in NOMES]
saidas = [amostras / (nome + '.encrypted') for nome in NOMES]
chave = simulador / 'chave_recuperacao.key'
```

As duas primeiras linhas usam **compreensão de lista**: para cada `nome` em `NOMES`, constroem um caminho. `arquivos` contém os originais; `saidas` contém os caminhos de destino com o sufixo `.encrypted`. A última linha define o caminho da chave.

A primeira compreensão equivale a:

```python
arquivos = []
for nome in NOMES:
    arquivos.append(amostras / nome)
```

`append(valor)` acrescenta um elemento ao final da lista. O método recebe um argumento: o elemento a adicionar.

### 5.4. Impedir entradas inválidas e substituições

```python
for arq, saida in zip(arquivos, saidas):
    if arq.is_symlink() or not arq.is_file() or saida.exists() or saida.is_symlink():
        raise RuntimeError('Amostra ausente ou resultado existente: ' + arq.name)
if chave.exists() or chave.is_symlink():
    raise RuntimeError('Já existe chave de recuperação. Preserve a chave anterior.')
```

`zip(arquivos, saidas)` recebe **duas sequências** e produz pares por posição. A cada volta do `for`, `arq` é o original e `saida` é o destino correspondente.

- `is_symlink()` verifica se o caminho é um link simbólico.
- `is_file()` verifica se corresponde a um arquivo regular.
- `exists()` verifica se o caminho existe.
- `or` une as verificações: uma condição verdadeira já provoca o erro.
- `arq.name` devolve apenas o nome do arquivo, usado na mensagem.

**Objetivo:** não processar amostras ausentes ou links simbólicos e não sobrescrever resultados ou chaves de testes anteriores. A validação ocorre antes da confirmação do usuário.

### 5.5. Solicitar confirmação

```python
print('Modo detectado:', modo)
print('Serão criadas cópias criptografadas; originais serão preservados.')
if input('Digite SIMULAR para continuar: ') != 'SIMULAR':
    print('Cancelado.')
    return
```

`print(...)` exibe valores no terminal; aceita um ou vários argumentos separados por vírgula. `input(mensagem)` mostra a mensagem e aguarda texto digitado, retornando uma **string**. A comparação é exata: `simular` não é igual a `SIMULAR`. Se a confirmação falhar, `return` encerra `main()` sem executar as etapas seguintes.

### 5.6. Criar backups sem substituir os existentes

```python
for arq in arquivos:
    destino = backup / arq.name
    if destino.is_symlink():
        raise RuntimeError('Backup inválido: ' + destino.name)
    if not destino.exists():
        shutil.copy2(str(arq), str(destino))
```

O `for` percorre cada original. `destino` é o caminho correspondente na pasta `backup`. Se for um link simbólico, o código lança erro. Se **não existir**, `shutil.copy2(...)` copia o arquivo.

**Parâmetros de `copy2(src, dst)`:**

| Parâmetro | Valor usado | Significado |
|---|---|---|
| `src` | `str(arq)` | Caminho do arquivo de origem |
| `dst` | `str(destino)` | Caminho onde a cópia será salva |

`str(...)` converte um objeto `Path` em texto. `copy2()` procura preservar metadados, como datas do arquivo, quando o sistema permite.

**Atenção:** um backup já existente é mantido sem comparação de conteúdo. Se uma cópia falhar depois de outras terem sido criadas, não existe rotina automática de desfazer.

### 5.7. Gerar e salvar a chave

```python
token = Fernet.generate_key()
with chave.open('xb') as f:
    f.write(token)
cifrador = Fernet(token)
```

- `Fernet.generate_key()` gera uma chave aleatória adequada ao Fernet; não recebe parâmetros.
- `chave.open('xb')` abre um arquivo para **criação exclusiva** (`x`) em modo **binário** (`b`). Falha se o arquivo já existir.
- `with ... as f` garante o fechamento do arquivo ao sair do bloco, mesmo se ocorrer uma exceção durante a gravação.
- `f.write(token)` recebe os bytes da chave e os grava no arquivo.
- `Fernet(token)` cria o objeto `cifrador`, configurado com a chave. O parâmetro `token` é a chave Fernet.

**Por que a chave é importante?** A descriptografia posterior exige a mesma chave. Perder a chave inviabiliza a recuperação normal dos arquivos criptografados.

### 5.8. Criptografar cópias

```python
for arq, saida in zip(arquivos, saidas):
    with saida.open('xb') as f:
        f.write(cifrador.encrypt(arq.read_bytes()))
    print('[CRIPTOGRAFADO EM CÓPIA]', arq.name)
print('Concluído. Originais e backups preservados.')
```

O programa percorre os pares de entrada e saída. Para cada par, cria um novo arquivo `.encrypted` e executa três operações **de dentro para fora**:

1. `arq.read_bytes()` lê **todo o conteúdo** do original como bytes; não recebe parâmetros.
2. `cifrador.encrypt(dados)` recebe esses bytes e retorna bytes criptografados.
3. `f.write(bytes_criptografados)` grava o resultado no arquivo de saída.

O modo `'xb'` evita substituir uma saída já existente. A mensagem `print()` é exibida após cada cópia. **O arquivo original continua onde estava**; não há `unlink()`, `remove()` ou substituição do original neste script.

**Limitação:** `read_bytes()` carrega o arquivo inteiro na memória; é adequado para pequenas amostras, mas não é ideal para arquivos muito grandes. Se uma falha ocorrer durante a escrita, podem restar arquivos parciais.

## 6. Bloco de inicialização e tratamento de erros

```python
if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
```

**`__name__`** é uma variável especial. Quando o arquivo é executado diretamente, costuma valer `'__main__'`; quando é importado como módulo, tem outro valor. Assim, o código não chama `main()` automaticamente durante uma importação.

**`try`** delimita o trecho em que exceções serão monitoradas. **`except Exception as erro`** captura exceções da família `Exception` e guarda o objeto na variável `erro`. `print('[ERRO]', erro)` mostra a mensagem. **`sys.exit(1)`** encerra com código de saída `1`, convencionado como falha. Um término normal costuma usar código `0`.

## 7. Exemplo prático da estrutura e dos resultados

Abaixo, um exemplo simplificado para o modo `laboratorio`:

```text
RansomwareLab/
├── amostras/
│   ├── clientes.txt                  <- original preservado
│   ├── clientes.txt.encrypted        <- nova cópia criptografada
│   ├── confidencial.txt
│   ├── confidencial.txt.encrypted
│   └── ...                           <- os outros três pares
├── backup/
│   ├── clientes.txt                  <- cópia de segurança
│   └── ...                           <- backups das demais amostras
└── simulador/
    ├── criptografar_beta.py
    └── chave_recuperacao.key         <- chave necessária para recuperar
```

No modo `desenvolvimento`, a função `localizar()` devolve como diretório-base a subpasta `testes/RansomwareLab` abaixo de `lab-ransomware`. O restante de `main()` trabalha com a mesma estrutura relativa (`amostras`, `backup`, `simulador`).

## 8. Glossário dos conceitos utilizados

| Conceito | Significado no programa |
|---|---|
| Função | Bloco reutilizável de instruções definido com `def` |
| Argumento | Valor passado na chamada, como `token` em `Fernet(token)` |
| Parâmetro | Nome que recebe o valor dentro da função ou método |
| Variável | Nome associado a um valor, como `lab` ou `modo` |
| Tupla | Sequência ordenada, usada em `NOMES` |
| Lista | Sequência mutável, usada em `arquivos` e `saidas` |
| `for` | Repete um bloco para cada elemento |
| `if` | Executa um bloco se uma condição for verdadeira |
| `return` | Encerra uma função e opcionalmente devolve valores |
| `raise` | Lança uma exceção |
| `try` / `except` | Permitem tratar falhas de execução |
| `with` | Gerencia a abertura e o fechamento de arquivos |
| Bytes | Representação binária dos dados lidos e gravados |
| `Path` | Objeto para manipular caminhos de arquivos |
| Fernet | Esquema de criptografia simétrica autenticada |

## 9. Pontos que merecem atenção no projeto

1. **O nome `modo` não controla ações diferentes:** ele apenas identifica e informa o ambiente. A criptografia funciona do mesmo modo nos dois caminhos.
2. **A preservação é intencional:** os arquivos originais não são apagados nem alterados; a saída é criada separadamente.
3. **Backups anteriores não são validados:** o programa não confere se os arquivos já existentes na pasta `backup` correspondem às amostras atuais.
4. **Não há reversão automática de falhas:** um erro após a criação de parte dos backups, da chave ou das saídas pode deixar resultados parciais.
5. **A chave fica em arquivo local:** a segurança e a recuperação dependem de proteger `chave_recuperacao.key`.
6. **`hashlib` está sem uso:** este script não calcula nem compara hashes.

**Conclusão:** `localizar()` responde **“onde devo trabalhar?”**; `main()` responde **“quais verificações e operações devo executar?”**; e o bloco `if __name__ == '__main__'` responde **“quando iniciar e como apresentar erros?”**. Essa separação torna o código mais fácil de estudar, testar e manter.
