# Pengyn Intelligence

Plataforma de inteligência operacional voltada à identificação de divergências, perdas e oportunidades a partir da análise de dados de diferentes fontes.

O projeto está sendo desenvolvido de forma incremental. A implementação atual concentra-se em um primeiro MVP de **conciliação de vendas e recebimentos**, utilizando arquivos CSV estruturados.

> **Encontre o que não fecha, entenda o que está acontecendo e descubra onde melhorar.**

## MVP atual

A versão atual implementa uma rotina de conciliação entre dois conjuntos de dados:

* **Vendas** — valores esperados a receber;
* **Recebimentos** — valores efetivamente recebidos.

Os registros são relacionados por meio do campo `external_id`.

A aplicação identifica:

* vendas conciliadas corretamente;
* vendas sem recebimento;
* recebimentos sem venda correspondente;
* divergências de valores;
* valor total das divergências encontradas.

O resultado é apresentado por meio de uma interface de linha de comando (CLI).

## Fluxo atual

```text
             vendas.csv
                 │
                 ▼
        ┌─────────────────┐
        │   Carregamento  │
        │   e validação   │
        └────────┬────────┘
                 │
                 │
                 ▼
        ┌─────────────────┐
        │   Conciliação   │◄──── recebimentos.csv
        │  por external_id│
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Classificação   │
        │ das divergências│
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │    Resumo da    │
        │    conciliação  │
        └─────────────────┘
```

## Regras de conciliação

Para cada `external_id`, a aplicação compara os valores encontrados nas duas fontes.

### Venda e recebimento com mesmo valor

O registro é considerado **conciliado**.

### Venda sem recebimento

O registro é identificado como:

```text
sales_without_receipt
```

### Recebimento sem venda correspondente

O registro é identificado como:

```text
receipts_without_sale
```

### Venda e recebimento com valores diferentes

O registro é classificado como:

```text
amount_mismatch
```

A diferença absoluta também é acumulada no total da divergência.

Os valores monetários são tratados em centavos utilizando `Decimal`, evitando problemas de precisão associados ao uso direto de números de ponto flutuante.

## Exemplo

Considerando:

```text
Vendas
external_id    expected_net
1001           100.00
1002           250.00
1003           300.00

Recebimentos
external_id    amount
1001           100.00
1002           240.00
1004           150.00
```

A conciliação identifica:

```text
A conciliação identifica:

1 venda conciliada
1 divergência de valor
1 venda sem recebimento
1 recebimento sem venda

A divergência financeira total neste exemplo é de R$ 460,00.
```

Além da quantidade de ocorrências, a aplicação calcula o valor financeiro total das divergências.

## Saída da aplicação

A aplicação pode ser executada através da CLI:

```bash
python -m pengyn_intelligence reconcile vendas.csv recebimentos.csv
```

O resultado apresenta um resumo semelhante a:

```text
Total sales: 4
Total receipts: 4
Matched sales: 2
Receipts without sale: 1
Sales without receipt: 1
Amount mismatches: 1
Total divergence: R$ 60.00
```

## Estrutura do projeto

```text
pengyn-intelligence/
│
├── docs/
│   └── product/
│       └── vision.md
│
├── src/
│   └── pengyn_intelligence/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── reconcile.py
│
├── tests/
│   ├── fixtures/
│   │   ├── recebimentos.csv
│   │   └── vendas.csv
│   │
│   ├── test_cli.py
│   └── test_reconcile.py
│
├── .gitignore
├── pyproject.toml
└── README.md
```

## Testes

O projeto possui testes automatizados cobrindo tanto a lógica de conciliação quanto a interface de linha de comando.

Entre os cenários testados estão:

* conciliação perfeita;
* venda sem recebimento;
* recebimento sem venda;
* divergência de valores;
* IDs duplicados;
* arquivos sem registros;
* colunas adicionais;
* espaços em `external_id`;
* valores zerados;
* IDs vazios;
* arquivos inexistentes;
* execução da CLI.

Para executar:

```bash
python -m pytest
```

Resultado atual:

```text
A suíte possui atualmente 15 testes automatizados, todos passando.
```

## Tecnologias

* Python 3.12+
* pytest
* argparse
* Decimal
* CSV
* setuptools

O projeto utiliza a estrutura `src/` e configuração baseada em `pyproject.toml`.

## Organização do código

A implementação mantém a lógica de negócio separada da interface de execução.

### `reconcile.py`

Contém a lógica principal de conciliação:

* leitura dos arquivos;
* validação dos cabeçalhos;
* tratamento dos valores monetários;
* comparação dos registros;
* classificação das divergências;
* geração do resumo.

### `cli.py`

Responsável pela interface de linha de comando:

```text
python -m pengyn_intelligence reconcile <vendas> <recebimentos>
```

### `tests/`

Contém testes unitários e de integração da CLI, além de arquivos utilizados como fixtures.

## Documentação do produto

A visão do produto está disponível em:

```text
docs/product/vision.md
```

Esse documento descreve a visão de longo prazo do Pengyn Intelligence, incluindo possíveis evoluções para:

* Data Quality;
* observabilidade;
* analytics;
* inteligência artificial;
* RAG;
* agentes especializados.

Essas capacidades fazem parte do **roadmap do produto** e não estão representadas como funcionalidades já implementadas neste MVP.

## Roadmap

A evolução planejada parte da conciliação básica para uma plataforma mais ampla de inteligência operacional.

Possíveis etapas futuras:

```text
MVP atual
   │
   ├── Conciliação
   ├── Identificação de divergências
   └── Testes automatizados
        │
        ▼
Data Quality
        │
        ▼
Persistência e histórico
        │
        ▼
Analytics e indicadores
        │
        ▼
Observabilidade e alertas
        │
        ▼
Inteligência Artificial
        │
        ├── Análise de divergências
        ├── Explicação de ocorrências
        ├── Perguntas em linguagem natural
        └── Recomendações
```

A implementação dessas etapas dependerá da evolução do produto e das necessidades identificadas ao longo do desenvolvimento.

## Objetivo técnico

Além da construção do produto, o projeto serve como laboratório para aplicar conceitos de engenharia de software e dados em um problema orientado ao negócio.

Entre os objetivos estão:

* modelar regras de negócio de forma testável;
* trabalhar com dados estruturados;
* separar lógica de negócio e interface;
* tratar valores financeiros com precisão;
* criar testes automatizados;
* construir uma aplicação Python executável por CLI;
* evoluir progressivamente a solução para uma arquitetura de dados mais completa.

## Status

**MVP funcional em desenvolvimento.**

A implementação atual está concentrada na conciliação de vendas e recebimentos a partir de arquivos CSV. Novas capacidades serão incorporadas de forma incremental conforme a evolução do produto.

---

**Pengyn Intelligence**
*Encontre o que não fecha, entenda o que está acontecendo e descubra onde melhorar.*
