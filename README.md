# TRF5 Scraper --- Scrapy

Coletor de dados de processos do **Tribunal Regional Federal da 5ª
Região (TRF5)** utilizando **Scrapy**, com suporte para consulta por
**número de processo** ou **CNPJ**.

------------------------------------------------------------------------

## 🔎 O que este scraper faz

Ele extrai automaticamente:

-   **Número do processo**
-   **Número do processo legado**
-   **Data de autuação**
-   **Relator**
-   **Envolvidos**
-   **Movimentações processuais**
-   **URL consultada**

------------------------------------------------------------------------

## 🚀 Como executar

### 1. Instale as dependências

``` bash
pip install scrapy
```

### 2. Rodando com número do processo
Você pode consultar um ou mais processos. Para múltiplos, separe os números por vírgula:

``` bash
# Um processo
scrapy crawl trf5 -a processo=0015648-78.1999.4.05.0000

# Múltiplos processos
scrapy crawl trf5 -a processo=0015648-78.1999.4.05.0000,0012656-90.2012.4.05.0000.
```

### 3. Rodando com CNPJ

``` bash
scrapy crawl trf5 -a cnpj=00000000000191
```

> O CNPJ pode ser informado com ou sem pontuação.

------------------------------------------------------------------------

## 🛠️ Decisões de Implementação

-   Uso de `start_requests()` para iniciar consulta por **processo** ou
    **CNPJ**.
-   Extração de dados usando **XPath + normalize-space()** para reduzir
    ruídos.
-   Estrutura HTML do TRF5 é variável → foram usados **XPaths
    flexíveis** e **regex** como fallback.
-   Criação de funções separadas para:
    -   Relator
    -   Envolvidos
    -   Movimentações
-   Consulta via CNPJ reproduz a requisição original do formulário
    (GET + POST).

------------------------------------------------------------------------

## 📌 Dificuldades e Soluções

### 1. HTML inconsistente

**Solução:** XPaths genéricos + regex complementar.

### 2. Formatos diferentes de número de processo

**Solução:** múltiplas regex + fallback para número legado.

### 3. Consulta por CNPJ sem endpoint direto

**Solução:** reprodução da requisição POST via `FormRequest`.

------------------------------------------------------------------------

## 📁 Estrutura do Projeto

    trf5/
    ├─ trf5/
    │  ├─ spiders/
    │  │  └─ trf5.py
    ├─ scrapy.cfg
    └─ README.md

------------------------------------------------------------------------

## 📦 Exemplo de saída

``` json
{
  "numero_processo": "0015648-78.1999.4.05.0000",
  "numero_legado": "99.015.648-8",
  "data_autuacao": "24-07-1999",
  "relator": "Desembargador Fulano de Tal",
  "envolvidos": [
    {"papel": "Autor", "nome": "FULANO"},
    {"papel": "Réu", "nome": "UNIÃO FEDERAL"}
  ],
  "movimentacoes": [
    {"data": "12/02/2024", "texto": "Juntada de petição"},
    {"data": "18/03/2024", "texto": "Conclusos ao Relator"}
  ],
  "url_origem": "https://www5.trf5.jus.br/processo/..."
}
```

------------------------------------------------------------------------

## 🧰 Tecnologias Utilizadas

-   Python 3
-   Scrapy
-   XPath
-   Regex

------------------------------------------------------------------------

## ✍️ Autor

**Adrianno Silva**
