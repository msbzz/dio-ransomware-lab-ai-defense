# Apostila comentada — `descriptografar_beta(1).py`

**Nível:** iniciante em Python  
**Contexto:** laboratório didático de criptografia e recuperação de arquivos  
**Base:** código original enviado, sem modificações.

> **Como ler esta apostila no VS Code:** abra este arquivo `.md` e use **Ctrl+Shift+V** para visualizar a prévia. Cada bloco de código foi delimitado por três crases e preserva a indentação do Python. As linhas indicadas correspondem ao arquivo `.py` original.

---

## 1. Qual é o objetivo do programa?

O `descriptografar_beta(1).py` é a parte de **recuperação** do experimento. Ele lê cinco arquivos terminados em `.encrypted`, utiliza a chave `chave_recuperacao.key` para recuperar seus conteúdos e confere se os arquivos originais já existem.

Ele foi planejado para trabalhar com os arquivos produzidos pelo `criptografar_beta(1).py`:

1. **Localiza** a estrutura de pastas do laboratório.
2. **Abre** a chave de recuperação.
3. **Valida e descriptografa os cinco arquivos em memória**, antes de solicitar confirmação.
4. **Pede autorização** ao usuário para continuar.
5. Para cada arquivo, **compara** o conteúdo recuperado com o original existente ou **recria** o original caso esteja ausente.
6. **Preserva** os arquivos `.encrypted`, a chave e os backups existentes.

**Importante:** ele não lê os backups para recuperar dados, não apaga os arquivos criptografados e não sobrescreve um arquivo original diferente. Também não garante uma operação integralmente reversível: uma falha durante a restauração pode ocorrer depois de alguns arquivos já terem sido recriados.

### 1.1. Exemplo visual da estrutura

```text
RansomwareLab/
├── amostras/
│   ├── clientes.txt                 ← original (pode estar ausente)
│   ├── clientes.txt.encrypted       ← arquivo criptografado
│   ├── confidencial.txt.encrypted
│   ├── contrato.txt.encrypted
│   ├── financeiro.txt.encrypted
│   └── interno.txt.encrypted
├── backup/                          ← backups preservados; não são lidos aqui
└── simulador/
    ├── descriptografar_beta.py
    └── chave_recuperacao.key        ← chave necessária para recuperar os dados
```

O programa espera cinco arquivos `.encrypted`, mesmo que os cinco arquivos originais ainda estejam presentes.

### 1.2. Relação com a criptografia

| Programa de criptografia | Programa de descriptografia |
|---|---|
| Gera a chave com `Fernet.generate_key()` | Lê a chave com `chave.read_bytes()` |
| Cria o objeto `Fernet(token)` | Cria o objeto `Fernet(chave.read_bytes())` |
| Usa `encrypt()` | Usa `decrypt()` |
| Cria arquivos `.encrypted` | Lê os arquivos `.encrypted` |
| Preserva os originais | Confere ou restaura os originais |

---

## 2. Código completo, com indentação preservada

```python
# -*- coding: utf-8 -*-
"""Recuperação didática: verifica e restaura cópias criptografadas."""
from pathlib import Path
import sys
from cryptography.fernet import Fernet, InvalidToken

NOMES = ('clientes.txt', 'confidencial.txt', 'contrato.txt', 'financeiro.txt', 'interno.txt')


def localizar():
    pasta = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
    if pasta.name.lower() != 'simulador':
        raise RuntimeError('Execute a partir de uma pasta chamada simulador.')
    if pasta.parent.name.lower() == 'ransomwarelab':
        return pasta.parent, 'laboratorio'
    if pasta.parent.name.lower() == 'lab-ransomware':
        return pasta.parent / 'testes' / 'RansomwareLab', 'desenvolvimento'
    raise RuntimeError('Caminho não reconhecido.')


def main():
    lab, modo = localizar()
    amostras = lab / 'amostras'
    chave = lab / 'simulador' / 'chave_recuperacao.key'
    if chave.is_symlink() or not chave.is_file() or not amostras.is_dir():
        raise RuntimeError('Chave ou pasta de amostras ausente.')
    cifrador = Fernet(chave.read_bytes())
    resultados = []
    for nome in NOMES:
        origem = amostras / (nome + '.encrypted')
        if origem.is_symlink() or not origem.is_file():
            raise RuntimeError('Arquivo criptografado ausente: ' + nome)
        try:
            dados = cifrador.decrypt(origem.read_bytes())
        except InvalidToken:
            raise RuntimeError('Chave inválida ou arquivo danificado: ' + nome)
        resultados.append((nome, dados))
    print('Modo detectado:', modo)
    print('Cinco arquivos validados. Os originais existentes não serão sobrescritos.')
    if input('Digite RECUPERAR para continuar: ') != 'RECUPERAR':
        print('Cancelado.')
        return
    # Se o original já existir, só verificamos seu conteúdo.
    # Se não existir, restauramos uma nova cópia, sem apagar o .encrypted.
    for nome, dados in resultados:
        destino = amostras / nome
        if destino.is_symlink():
            raise RuntimeError('Destino inválido: ' + nome)
        if destino.exists():
            if destino.read_bytes() != dados:
                raise RuntimeError('Original diferente; não sobrescrever: ' + nome)
            print('[CONFERIDO]', nome)
        else:
            with destino.open('xb') as f:
                f.write(dados)
            print('[RECUPERADO]', nome)
    print('Concluído. Arquivos .encrypted, backups e chave preservados.')


if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
```

---

## 3. Bibliotecas e configuração inicial — linhas 1 a 7

### Linha 1 — Codificação

```python
# -*- coding: utf-8 -*-
```

O `#` inicia um comentário. A indicação `utf-8` documenta a codificação do arquivo-fonte, que permite acentos e outros caracteres Unicode. No Python 3, UTF-8 já é a codificação padrão para o código-fonte.

### Linha 2 — Descrição do módulo

```python
"""Recuperação didática: verifica e restaura cópias criptografadas."""
```

As três aspas criam uma **docstring**: uma descrição associada ao módulo. Ela explica a finalidade do arquivo e pode ser consultada por ferramentas de documentação.

### Linha 3 — `Path`

```python
from pathlib import Path
```

- `from`: indica a biblioteca da qual vamos importar algo.
- `pathlib`: biblioteca padrão para trabalhar com caminhos.
- `import`: importa um recurso.
- `Path`: classe usada para representar caminhos de arquivos e diretórios.

Exemplo independente:

```python
from pathlib import Path
arquivo = Path('C:/RansomwareLab/amostras/clientes.txt')
print(arquivo.name)  # clientes.txt
```

### Linha 4 — `sys`

```python
import sys
```

Importa recursos do ambiente de execução do Python. Neste código são utilizados `sys.executable` (caminho do executável) e `sys.exit(1)` (encerramento indicando erro).

### Linha 5 — `Fernet` e `InvalidToken`

```python
from cryptography.fernet import Fernet, InvalidToken
```

- `cryptography`: biblioteca externa que precisa estar instalada no ambiente Python.
- `fernet`: módulo com criptografia simétrica autenticada.
- `Fernet`: classe que recebe uma chave e oferece `encrypt()` e `decrypt()`.
- `InvalidToken`: exceção que indica que um token não pôde ser autenticado/descriptografado, por exemplo por chave incorreta ou conteúdo alterado.

**Diferença:** `Fernet` é utilizado para realizar a operação; `InvalidToken` é utilizado para reconhecer uma falha específica da operação.

### Linha 7 — Nomes esperados

```python
NOMES = ('clientes.txt', 'confidencial.txt', 'contrato.txt', 'financeiro.txt', 'interno.txt')
```

`NOMES` é uma **tupla**, uma sequência de valores. Cada item é uma string (texto). Os parênteses delimitam a sequência, as vírgulas separam os elementos e as aspas identificam os textos. O programa percorre esses nomes, na ordem indicada, para localizar os cinco arquivos criptografados.

---

## 4. Função `localizar()` — linhas 10 a 18

### Qual é o objetivo desta função?

Ela **descobre em qual estrutura de pastas o programa está instalado** e retorna dois dados: o diretório-base do laboratório e o nome do modo detectado. A função não descriptografa nada e não abre arquivos de amostra.

**Assinatura:** `localizar()` não recebe argumentos. **Retorno:** dois valores, `(caminho_do_lab, modo)`. **Erros possíveis:** `RuntimeError` se a estrutura de nomes de pastas não corresponder às condições programadas.

```python
def localizar():
    pasta = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
    if pasta.name.lower() != 'simulador':
        raise RuntimeError('Execute a partir de uma pasta chamada simulador.')
    if pasta.parent.name.lower() == 'ransomwarelab':
        return pasta.parent, 'laboratorio'
    if pasta.parent.name.lower() == 'lab-ransomware':
        return pasta.parent / 'testes' / 'RansomwareLab', 'desenvolvimento'
    raise RuntimeError('Caminho não reconhecido.')
```

### Linha 10 — `def localizar():`

- `def` significa **definir uma função**.
- `localizar` é o nome pelo qual o restante do programa a chama.
- `()` vazio significa que nenhum argumento precisa ser informado.
- `:` introduz o bloco de instruções da função.
- As linhas recuadas abaixo dela pertencem à função: esse recuo é a **indentação** do Python.

### Linha 11 — Descobrir a pasta do programa

```python
pasta = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
```

Essa linha reúne várias operações. Uma forma didática de entendê-la é separá-la em etapas (o exemplo abaixo **explica** a linha, não substitui o código original):

```python
empacotado = getattr(sys, 'frozen', False)
caminho_programa = sys.executable if empacotado else __file__
pasta = Path(caminho_programa).resolve().parent
```

**Parâmetros e métodos:**

| Elemento | Papel na expressão |
|---|---|
| `getattr(objeto, nome, padrão)` | Obtém o atributo `nome` de `objeto`; usa `padrão` se não existir |
| `sys` | Objeto consultado por `getattr` |
| `'frozen'` | Nome do atributo que costuma indicar empacotamento em executável |
| `False` | Valor padrão quando o atributo não existe |
| `sys.executable` | Caminho do executável do processo atual |
| `__file__` | Caminho do arquivo Python atual |
| `A if condição else B` | Escolhe `A` quando a condição é verdadeira, ou `B` caso contrário |
| `Path(caminho)` | Constrói um objeto de caminho |
| `.resolve()` | Resolve o caminho para uma forma absoluta |
| `.parent` | Obtém a pasta que contém o arquivo |

**Exemplo:** se o script estiver em `C:\RansomwareLab\simulador\descriptografar_beta.py`, a variável `pasta` será a pasta `C:\RansomwareLab\simulador`.

### Linhas 12 e 13 — Verificar o nome da pasta

```python
if pasta.name.lower() != 'simulador':
    raise RuntimeError('Execute a partir de uma pasta chamada simulador.')
```

- `if` testa uma condição.
- `.name` obtém o último componente do caminho (aqui, o nome da pasta).
- `.lower()` converte o texto para minúsculas.
- `!=` significa **diferente de**.
- `raise` provoca uma exceção.
- `RuntimeError('mensagem')` cria uma exceção com a mensagem indicada.

**Objetivo:** impedir que o programa continue se não estiver dentro de uma pasta chamada `simulador`, desconsiderando diferenças entre maiúsculas e minúsculas no nome.

### Linhas 14 e 15 — Modo laboratório

```python
if pasta.parent.name.lower() == 'ransomwarelab':
    return pasta.parent, 'laboratorio'
```

`==` significa **igual a**. Se a pasta acima de `simulador` for `RansomwareLab`, `return` encerra a função e devolve dois valores: a pasta superior e o texto `'laboratorio'`.

### Linhas 16 e 17 — Modo desenvolvimento

```python
if pasta.parent.name.lower() == 'lab-ransomware':
    return pasta.parent / 'testes' / 'RansomwareLab', 'desenvolvimento'
```

Quando a pasta superior se chama `lab-ransomware`, o programa monta um caminho para `testes/RansomwareLab` e devolve o modo `'desenvolvimento'`.

**Atenção ao operador `/`:** entre objetos `Path` e textos, ele **une componentes de um caminho**. Não é divisão numérica.

### Linha 18 — Caminho não reconhecido

```python
raise RuntimeError('Caminho não reconhecido.')
```

Se a função chegar até aqui, nenhuma condição anterior retornou um resultado. Por isso é gerado um erro.

**Limitação importante:** a função verifica nomes e posições de pastas, mas não confirma a identidade do computador nem comprova que se trata de um laboratório confiável. O modo detectado é apenas mostrado na tela; não altera a lógica de recuperação.

---

## 5. Função `main()` — linhas 21 a 57

### Qual é o objetivo desta função?

`main()` é a **função principal**, responsável por coordenar a recuperação. Ela chama `localizar()`, prepara caminhos, carrega a chave, descriptografa e valida os cinco arquivos, pede confirmação e decide se deve conferir ou restaurar cada original.

**Assinatura:** `main()` não recebe parâmetros. **Retorno:** não retorna dados úteis; pode terminar normalmente ou antecipadamente com `return`. **Possíveis falhas:** arquivos ausentes, chave inválida, arquivo criptografado danificado, original diferente, falha de leitura/gravação e outras exceções.

### Linha 21 — Definir a função

```python
def main():
```

`def` cria a função. O nome `main` é uma convenção comum para a rotina principal. Os parênteses vazios mostram que ela não exige argumentos.

### Linha 22 — Receber os valores de `localizar()`

```python
lab, modo = localizar()
```

A função `localizar()` devolve dois valores, que são atribuídos às variáveis `lab` e `modo`. Isso é chamado **desempacotamento**.

Exemplo didático:

```python
lab, modo = ('C:/RansomwareLab', 'laboratorio')
```

No programa real, `lab` é um objeto `Path`, não apenas uma string.

### Linha 23 — Definir a pasta de amostras

```python
amostras = lab / 'amostras'
```

Monta o caminho para a pasta de arquivos originais e criptografados.

### Linha 24 — Definir a localização da chave

```python
chave = lab / 'simulador' / 'chave_recuperacao.key'
```

Monta o caminho do arquivo de chave. Ainda **não lê** a chave: apenas registra onde ela deve estar.

### Linhas 25 e 26 — Validar a estrutura

```python
if chave.is_symlink() or not chave.is_file() or not amostras.is_dir():
    raise RuntimeError('Chave ou pasta de amostras ausente.')
```

| Elemento | Significado |
|---|---|
| `chave.is_symlink()` | Verdadeiro quando o caminho da chave é um link simbólico |
| `chave.is_file()` | Verdadeiro quando a chave é um arquivo comum |
| `amostras.is_dir()` | Verdadeiro quando a pasta de amostras é um diretório |
| `not` | Inverte um valor lógico (`True`/`False`) |
| `or` | Basta uma condição verdadeira para o `if` ser verdadeiro |

**Objetivo:** interromper a recuperação se a chave for um link simbólico, não for um arquivo ou se a pasta de amostras não existir como diretório.

### Linha 27 — Ler a chave e criar o cifrador

```python
cifrador = Fernet(chave.read_bytes())
```

Essa linha tem duas etapas:

1. `chave.read_bytes()` abre o arquivo indicado por `chave`, lê todo o seu conteúdo em **bytes** e devolve esses bytes.
2. `Fernet(...)` recebe a chave lida e cria um objeto capaz de descriptografar tokens Fernet produzidos com a chave correspondente.

**Parâmetro de `Fernet`:** uma chave Fernet válida em bytes. Uma chave malformada pode causar erro antes de começar a descriptografar.

**Importante:** ler a chave não significa descriptografar os arquivos; isso ocorrerá na linha 34.

### Linha 28 — Preparar a lista de resultados

```python
resultados = []
```

`[]` cria uma **lista vazia**. Ela guardará pares `(nome, dados_recuperados)` após a descriptografia de cada arquivo.

### Linha 29 — Percorrer os nomes

```python
for nome in NOMES:
```

`for` inicia uma repetição. A cada volta, `nome` recebe o próximo elemento da tupla `NOMES`.

### Linha 30 — Montar o nome do arquivo criptografado

```python
origem = amostras / (nome + '.encrypted')
```

`nome + '.encrypted'` concatena textos. Por exemplo, `clientes.txt` torna-se `clientes.txt.encrypted`. O `/` une esse nome ao caminho da pasta `amostras`.

### Linhas 31 e 32 — Verificar a origem

```python
if origem.is_symlink() or not origem.is_file():
    raise RuntimeError('Arquivo criptografado ausente: ' + nome)
```

Confere se o caminho é um arquivo comum e não um link simbólico. Se a condição falhar, gera um erro com o nome do arquivo esperado.

### Linha 33 — Iniciar o tratamento de erro

```python
try:
```

`try` indica um bloco no qual uma exceção específica poderá ser tratada. O código recuado abaixo pertence ao bloco.

### Linha 34 — Descriptografar

```python
dados = cifrador.decrypt(origem.read_bytes())
```

**Esta é a operação central do programa.** A avaliação ocorre de dentro para fora:

1. `origem.read_bytes()` lê todos os bytes do arquivo `.encrypted`.
2. `cifrador.decrypt(...)` tenta autenticar e descriptografar esses bytes com a chave carregada.
3. Se a operação tiver sucesso, o conteúdo original em bytes é atribuído a `dados`.

**Parâmetro de `decrypt`:** um token Fernet em bytes. **Retorno:** bytes do conteúdo original. **Erro relevante:** `InvalidToken` quando o token não é válido para a chave ou falha na validação.

Exemplo conceitual:

```python
conteudo_criptografado = origem.read_bytes()
conteudo_recuperado = cifrador.decrypt(conteudo_criptografado)
```

O programa faz essas duas operações em uma única linha.

### Linhas 35 e 36 — Tratar falha na descriptografia

```python
except InvalidToken:
    raise RuntimeError('Chave inválida ou arquivo danificado: ' + nome)
```

- `except InvalidToken` captura **especificamente** a exceção `InvalidToken`.
- `raise RuntimeError(...)` gera uma nova exceção com uma mensagem mais compreensível para o usuário.
- `+ nome` acrescenta o nome do arquivo problemático.

**Por que tratar esse erro?** Para explicar que o conteúdo não pôde ser recuperado com sucesso. Isso pode acontecer por chave incorreta, token adulterado ou arquivo danificado. Outros tipos de erro, como problemas de leitura, não são capturados por esse `except` específico.

### Linha 37 — Guardar o resultado

```python
resultados.append((nome, dados))
```

`append(item)` é um método de listas: acrescenta **um elemento ao final**. Aqui, o elemento é a tupla `(nome, dados)`.

Exemplo didático:

```python
resultados = []
resultados.append(('clientes.txt', b'conteudo recuperado'))
```

O prefixo `b` representa bytes. A lista conserva os conteúdos recuperados em memória até a fase de confirmação e gravação.

**Por que essa lista é importante?** Porque os cinco arquivos são descriptografados **antes** de qualquer tentativa de restaurar os originais. Se um deles apresentar `InvalidToken`, a etapa de gravação nem começa.

### Linhas 38 e 39 — Informar o resultado da validação

```python
print('Modo detectado:', modo)
print('Cinco arquivos validados. Os originais existentes não serão sobrescritos.')
```

`print()` escreve valores no terminal. Na primeira linha recebe dois argumentos, separados por vírgula, e os exibe com um espaço entre eles por padrão.

**Significado de “validados” aqui:** os cinco arquivos criptografados foram localizados e descriptografados com sucesso. Os arquivos originais ainda não foram comparados nessa etapa.

### Linhas 40 a 42 — Solicitar autorização

```python
if input('Digite RECUPERAR para continuar: ') != 'RECUPERAR':
    print('Cancelado.')
    return
```

`input(mensagem)` mostra o texto e aguarda o usuário digitar uma resposta, devolvendo uma **string**. `!=` significa “diferente de”. Se a resposta não for exatamente `RECUPERAR`, o programa mostra `Cancelado.` e `return` encerra `main()`.

A comparação diferencia maiúsculas de minúsculas: `recuperar` não é igual a `RECUPERAR`.

### Linhas 43 e 44 — Comentários explicativos

```python
# Se o original já existir, só verificamos seu conteúdo.
# Se não existir, restauramos uma nova cópia, sem apagar o .encrypted.
```

São comentários, não comandos executados. Eles explicam a regra adotada pelo programa para evitar sobrescrever originais.

### Linha 45 — Percorrer os dados recuperados

```python
for nome, dados in resultados:
```

Cada item da lista `resultados` contém uma tupla com dois elementos. O `for` desempacota cada tupla nas variáveis `nome` e `dados`.

### Linha 46 — Definir o destino

```python
destino = amostras / nome
```

Monta o caminho do arquivo original a ser conferido ou restaurado. Diferentemente da origem, esse caminho **não** tem o sufixo `.encrypted`.

### Linhas 47 e 48 — Rejeitar destino simbólico

```python
if destino.is_symlink():
    raise RuntimeError('Destino inválido: ' + nome)
```

Impede que o programa prossiga com um destino que seja link simbólico.

### Linha 49 — Verificar se o original existe

```python
if destino.exists():
```

`exists()` devolve `True` se o caminho existe e `False` se não existe. Isso determina qual dos dois caminhos o programa seguirá: **conferência** ou **recuperação**.

### Linhas 50 e 51 — Comparar os conteúdos

```python
if destino.read_bytes() != dados:
    raise RuntimeError('Original diferente; não sobrescrever: ' + nome)
```

`destino.read_bytes()` lê o arquivo original existente. `!= dados` compara seus bytes com o conteúdo recuperado da versão criptografada.

- **Iguais:** o arquivo original já tem o conteúdo esperado; não precisa ser regravado.
- **Diferentes:** gera erro e não sobrescreve esse arquivo.

Essa é uma comparação de **conteúdo**, não de nome, tamanho isolado ou data de modificação.

### Linha 52 — Indicar conferência

```python
print('[CONFERIDO]', nome)
```

Informa que o original já existia e que seus bytes coincidem com os bytes descriptografados.

### Linha 53 — Caso o original não exista

```python
else:
```

O `else` pertence ao `if destino.exists()` da linha 49. Portanto, só é executado quando o caminho do original **não existe**.

### Linha 54 — Criar arquivo novo

```python
with destino.open('xb') as f:
```

- `with` gerencia o recurso e fecha o arquivo ao sair do bloco.
- `destino.open(modo)` abre o caminho para a operação desejada.
- `'x'` significa **criar um arquivo novo**, falhando se já existir.
- `'b'` significa **modo binário**, adequado para bytes.
- `as f` atribui o arquivo aberto à variável `f`.

O modo `'xb'` reforça a regra de não sobrescrever um arquivo existente.

### Linha 55 — Gravar os bytes recuperados

```python
f.write(dados)
```

`write(conteudo)` grava o argumento no arquivo aberto. Como o arquivo foi aberto em modo binário, `dados` deve ser bytes — exatamente o tipo retornado por `decrypt()`.

### Linha 56 — Indicar recuperação

```python
print('[RECUPERADO]', nome)
```

Informa que um novo arquivo original foi criado com os bytes recuperados.

### Linha 57 — Mensagem de conclusão

```python
print('Concluído. Arquivos .encrypted, backups e chave preservados.')
```

Exibe uma mensagem depois que o laço termina sem erros. O código não contém comandos para apagar os `.encrypted`, os backups ou a chave.

---

## 6. Inicialização e tratamento de erros — linhas 60 a 65

```python
if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
```

### Linha 60 — Executar apenas como programa principal

`__name__` é uma variável especial. Quando o arquivo Python é executado diretamente, ela normalmente vale `'__main__'`. O teste `==` verifica essa igualdade. Se o arquivo for importado como módulo, a função principal não será executada automaticamente por esse bloco.

### Linha 61 — `try`

Inicia o bloco protegido pelo tratamento de exceções.

### Linha 62 — `main()`

Chama a função principal, que coordena todo o processo.

### Linha 63 — `except Exception as erro`

Captura exceções derivadas de `Exception` que ocorrerem no bloco `try`. O objeto da exceção é armazenado na variável `erro`.

### Linha 64 — `print('[ERRO]', erro)`

Mostra a indicação `[ERRO]` e a mensagem da exceção no terminal.

### Linha 65 — `sys.exit(1)`

Solicita o encerramento do processo com código de saída `1`, convencionalmente usado para indicar falha. O valor `0` costuma indicar conclusão normal.

---

## 7. Fluxo completo de execução

```text
INÍCIO
  │
  ▼
Verifica se o arquivo foi executado diretamente
  │
  ▼
main() chama localizar()
  │
  ▼
Identifica pasta-base e modo
  │
  ▼
Verifica a chave e a pasta amostras
  │
  ▼
Carrega a chave e cria Fernet(...)
  │
  ▼
Para cada um dos cinco arquivos .encrypted:
  ├── verifica se o arquivo existe
  ├── lê os bytes
  ├── tenta descriptografar
  └── guarda (nome, dados) em resultados
  │
  ▼
Todos os cinco foram recuperados em memória?
  ├── NÃO → erro, sem iniciar a restauração
  └── SIM
        │
        ▼
Solicita digitar RECUPERAR
  ├── resposta diferente → cancelamento
  └── resposta correta
        │
        ▼
Para cada (nome, dados):
  ├── destino é link simbólico → erro
  ├── original existe e é igual → [CONFERIDO]
  ├── original existe e é diferente → erro
  └── original ausente → cria arquivo → [RECUPERADO]
        │
        ▼
Mensagem de conclusão
```

---

## 8. Três situações práticas

### Situação A — Original já existe e está correto

```text
amostras/clientes.txt
amostras/clientes.txt.encrypted
```

O programa descriptografa a versão `.encrypted` e compara os bytes com `clientes.txt`. Se forem iguais, apresenta:

```text
[CONFERIDO] clientes.txt
```

Nenhuma substituição é realizada.

### Situação B — Original não existe

```text
amostras/clientes.txt.encrypted
```

Após a validação dos cinco arquivos e a confirmação do usuário, o programa cria `clientes.txt` com o conteúdo recuperado:

```text
[RECUPERADO] clientes.txt
```

O arquivo `.encrypted` permanece na pasta.

### Situação C — Original existe, mas é diferente

Se `clientes.txt` existir com bytes diferentes daqueles recuperados, o programa mostra um erro semelhante a:

```text
[ERRO] Original diferente; não sobrescrever: clientes.txt
```

Ele **não substitui** esse original. Se a diferença for encontrada depois de outros arquivos terem sido recriados, essas recuperações anteriores permanecem feitas.

---

## 9. Glossário de funções, métodos e operadores usados

| Recurso | Argumentos ou uso | Resultado / objetivo |
|---|---|---|
| `localizar()` | Nenhum | Devolve caminho-base e modo |
| `main()` | Nenhum | Coordena a execução; sem retorno útil |
| `getattr(obj, nome, padrão)` | Objeto, nome do atributo e valor padrão | Obtém atributo ou valor padrão |
| `Path(caminho)` | String ou caminho compatível | Objeto de caminho |
| `.resolve()` | Nenhum neste uso | Caminho absoluto resolvido |
| `.parent` | Propriedade, sem `()` | Diretório superior |
| `.name` | Propriedade, sem `()` | Último componente do caminho |
| `.lower()` | Nenhum | Texto em minúsculas |
| `.is_symlink()` | Nenhum | `True`/`False` para link simbólico |
| `.is_file()` | Nenhum | `True`/`False` para arquivo comum |
| `.is_dir()` | Nenhum | `True`/`False` para diretório |
| `.exists()` | Nenhum | `True`/`False` para existência do caminho |
| `.read_bytes()` | Nenhum | Conteúdo completo em bytes |
| `Fernet(chave)` | Chave Fernet em bytes | Objeto cifrador |
| `.decrypt(token)` | Token Fernet em bytes | Conteúdo descriptografado em bytes |
| `[].append(item)` | Um item | Adiciona elemento à lista |
| `.open('xb')` | Modo de abertura | Cria novo arquivo binário, sem sobrescrever |
| `.write(dados)` | Bytes | Grava bytes no arquivo |
| `print(...)` | Um ou mais valores | Exibe valores no terminal |
| `input(mensagem)` | Mensagem de orientação | Texto digitado pelo usuário |
| `RuntimeError(mensagem)` | Texto explicativo | Objeto de exceção |
| `sys.exit(1)` | Código de saída | Encerra indicando erro |
| `if` / `else` | Condição / alternativa | Escolha de fluxo |
| `for ... in ...` | Sequência | Repetição |
| `try` / `except` | Bloco / exceção | Tratamento de falhas |
| `raise` | Exceção | Provoca erro |
| `return` | Opcionalmente valores | Encerra a função |
| `==` / `!=` | Dois valores | Compara igualdade / diferença |
| `not` / `or` | Valores lógicos | Negação / alternativa lógica |
| `/` com `Path` | Partes de caminho | Junta componentes de caminho |
| `+` com strings | Textos | Concatena textos |

---

## 10. Cuidados e limitações reais do código

1. **A chave precisa ser compatível.** O arquivo `.key` deve conter uma chave Fernet válida e correspondente aos tokens criptografados.
2. **A validação inicial não grava arquivos.** Todos os cinco `.encrypted` são descriptografados em memória antes de solicitar `RECUPERAR`.
3. **O programa pode consumir memória proporcional ao tamanho dos arquivos.** `read_bytes()` lê arquivos inteiros e `resultados` mantém os conteúdos recuperados na memória.
4. **Os backups não são utilizados.** O programa preserva a pasta `backup`, mas não consulta nem restaura dados a partir dela.
5. **Não há rollback.** Se uma restauração intermediária falhar, arquivos já recriados não são automaticamente removidos.
6. **Arquivos originais diferentes não são sobrescritos.** Essa regra é aplicada por comparação de bytes.
7. **O modo detectado é informativo.** Os dois ambientes usam a mesma lógica de recuperação.
8. **A detecção de caminho não é uma barreira de segurança absoluta.** Ela depende de nomes e posições de diretórios.
9. **Falhas de leitura ou gravação também podem ocorrer.** O `except InvalidToken` trata apenas erros de token Fernet; outros erros são tratados pelo `except Exception` final.

---

## 11. Conclusão — o que o iniciante deve compreender

O programa demonstra como organizar uma aplicação Python em **funções com responsabilidades distintas**: `localizar()` determina os caminhos e `main()` coordena a recuperação. Também demonstra o uso de bibliotecas, objetos `Path`, listas, tuplas, laços `for`, condições `if`/`else`, tratamento de exceções e operações binárias com arquivos.

O conceito central é que **descriptografar não significa automaticamente substituir arquivos**. Primeiro, o programa recupera os bytes em memória; depois, com autorização, verifica se o original já está correto ou cria uma nova cópia somente quando necessário.

**Fim da apostila.**
