
# 📊 Relatório do Projeto  
## ALPCD – Grupo 09

### 👥 Membros do Grupo
- **Emanuel Paredinha** — A106827  
- **Tomás Bourbon** — A106824  
- **Simão Pedro** — A102520  

---

## 1. Introdução

O presente projeto consiste no desenvolvimento de uma **aplicação de linha de comandos (CLI)** em Python, destinada à recolha, análise e apresentação de informação sobre ofertas de emprego na área das **Tecnologias de Informação (IT)**.

A aplicação integra duas fontes principais de dados:

- **API pública do ITJobs.pt**  
  Utilizada para a obtenção estruturada e massiva de anúncios de emprego.

- **Plataforma Teamlyzer**  
  Da qual é efetuado **Web Scraping** para recolha de informação adicional sobre empresas, nomeadamente avaliações, descrições, salários e benefícios.

O projeto encontra-se dividido em dois grandes blocos funcionais, correspondentes às etapas de avaliação **TP1** e **TP2**.

---

## 2. Tecnologias Utilizadas

O projeto foi desenvolvido integralmente em **Python**, recorrendo às seguintes bibliotecas externas, escolhidas pela sua eficiência e robustez:

- **Typer** – Criação da interface de linha de comandos (CLI) e gestão de argumentos/opções  
- **Requests** – Comunicação HTTP com a API REST e obtenção de páginas HTML  
- **BeautifulSoup (bs4)** – Parsing e extração de dados (Web Scraping) do HTML do Teamlyzer  
- **Rich** – Apresentação visual de dados no terminal (tabelas formatadas e cores)  
- **Datetime** – Manipulação, comparação e formatação de datas  
- **re (Regex)** – Expressões regulares para deteção de padrões textuais (skills e regimes de trabalho)  
- **CSV / JSON** – Bibliotecas nativas para serialização e exportação de dados  

---

## 3. Arquitetura da Aplicação

A aplicação segue uma **estrutura modular**, facilitando a manutenção e a reutilização de código.

### 3.1 Configurações Globais

- Definição centralizada da **API Key do ITJobs**
- Configuração de **Headers HTTP**, incluindo um *User-Agent* específico (`TeamlyzerScraper`), de forma a evitar bloqueios durante o scraping

### 3.2 Funções Auxiliares

Para evitar repetição de código, foram implementadas várias funções genéricas:

- `request_api()` – Função central de acesso à API, com lógica de **paginação automática**
- `get_soup_teamlyzer()` – Realiza pedidos HTTP e converte o HTML em objetos BeautifulSoup
- `limpar_texto_html()` – Remove tags HTML e normaliza espaços em branco
- `cria_csv()` – Exporta listas de dicionários para ficheiros CSV

---

## 4. Funcionalidades – TP1 (API ITJobs)

### 4.1 Top N Ofertas (`top`)
Obtém as **N ofertas de emprego mais recentes**, permitindo:
- Visualização em JSON  
- Apresentação em tabela formatada (`--pretty`)  
- Exportação para CSV  

### 4.2 Pesquisa Filtrada (`search`)
Pesquisa vagas aplicando filtros cumulativos:
- Empresa  
- Localidade  
- Regime de trabalho **Part-time**

### 4.3 Identificação do Regime de Trabalho (`type`)
Dado o ID de uma vaga, o sistema analisa o título e o corpo do anúncio utilizando **expressões regulares**, classificando o regime como:
- Remoto  
- Híbrido  
- Presencial / Outro  

### 4.4 Análise Temporal de Skills (`skills`)
Conta a frequência de tecnologias pré-definidas (Python, SQL, Java, etc.) em vagas publicadas num intervalo de datas especificado pelo utilizador.

---

## 5. Funcionalidades – TP2 (Web Scraping)

### 5.1 Detalhe da Oferta Enriquecido (`get`)
Obtém os detalhes técnicos de uma vaga através da API do ITJobs e cruza essa informação com o Teamlyzer, adicionando:
- Rating da empresa  
- Descrição institucional  
- Salários médios  
- Benefícios reportados  

### 5.2 Estatísticas por Zona Geográfica (`statistics`)
Gera estatísticas agregadas, contabilizando o número de vagas por:
- Zona geográfica  
- Tipo de contrato  

Os resultados são exportados automaticamente para o ficheiro `estatisticas_zona.csv`.

### 5.3 Top Skills no Teamlyzer (`list-skills`)
Acede à página de empregos do Teamlyzer para um cargo específico (ex.: *Data Scientist*) e extrai as **skills mais frequentes**, permitindo identificar tendências do mercado.

---

## 6. Tratamento de Erros e Robustez

O código foi desenvolvido com foco na estabilidade:

- Utilização de blocos `try-except` para capturar falhas de rede ou erros na API  
- Verificação da existência de dados antes de aceder a chaves de dicionários  
- Feedback claro ao utilizador em caso de parâmetros inválidos ou ausência de resultados  

---

## 7. Conclusão

Este projeto cumpre todos os objetivos propostos, demonstrando a capacidade de integrar **APIs REST** com técnicas de **Web Scraping**, resultando numa ferramenta de análise de dados **funcional, modular e útil** para a análise do mercado de trabalho na área das Tecnologias de Informação.




tp1

a)python projeto.py top 5 --pretty
b)python projeto.py search Porto "Dellent" 3 --pretty
c)python projeto.py type 506847
d)python projeto.py skills 2025-11-01 2025-11-15
e)python projeto.py top 20 --csv ,,, python projeto.py search Porto "Dellent" 3 --csv


tp2

a)python projeto.py get 506837
b)python projeto.py statistics
c)python projeto.py list-skills "python"
d)python projeto.py list-skills "python" --csv ,,, python projeto.py get 506837 --csv


O projeto completo esta no projeto.py , a descriçao é que nao esta correta.