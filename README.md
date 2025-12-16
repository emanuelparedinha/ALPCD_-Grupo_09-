
Relatorio Projeto:
# ALPCD_-Grupo_09-
## Membros do grupo
- Emanuel Paredinha — A106827
- Tomás Bourbon  — A106824
- Simão Pedro — A102520


1. Introdução:
O presente projeto consiste no desenvolvimento de uma aplicação de linha de comandos (CLI) em Python, destinada à recolha, análise e apresentação de informação sobre ofertas de emprego na área das Tecnologias de Informação (IT).

A aplicação integra duas fontes principais de dados:

API pública do ItJobs.pt: Utilizada para a obtenção estruturada e massiva de anúncios de emprego.

Plataforma Teamlyzer: Da qual é efetuado Web Scraping para recolha de informação adicional sobre empresas (avaliações, descrições, salários e benefícios).

O projeto encontra-se dividido em dois grandes blocos funcionais que correspondem às etapas de avaliação (TP1 e TP2).

2. Tecnologias Utilizadas:
O projeto foi desenvolvido integralmente em Python, recorrendo às seguintes bibliotecas externas, escolhidas pela sua eficiência e robustez:

Typer: Criação da interface de linha de comandos (CLI) e gestão de argumentos/opções.

Requests: Comunicação HTTP com a API REST e obtenção de páginas HTML.

BeautifulSoup (bs4): Parsing e extração de dados (scraping) do HTML do Teamlyzer.

Rich: Apresentação visual de dados no terminal (tabelas formatadas e cores).

Datetime: Manipulação, comparação e formatação de datas.

Re (Regex): Expressões regulares para deteção de padrões textuais (skills e regimes de trabalho).

CSV / JSON: Bibliotecas nativas para serialização e exportação de dados.

3. Arquitetura da Aplicação:
A aplicação segue uma estrutura modular para facilitar a manutenção e reutilização de código:

3.1 Configurações Globais:
Definição centralizada da API Key do ItJobs.

Configuração de Headers HTTP (incluindo o User-Agent específico TeamlyzerScraper) para evitar bloqueios durante o scraping.

3.2 Funções Auxiliares:
Para evitar repetição de código, foram implementadas funções genéricas:

request_api(): Função central de acesso à API que implementa a lógica de paginação automática, permitindo obter mais resultados do que o limite padrão da API.

get_soup_teamlyzer(): Função resiliente para realizar pedidos HTTP e converter o HTML em objetos BeautifulSoup.

limpar_texto_html(): Utilitário para remover tags HTML e normalizar espaços em branco nas descrições.

cria_csv(): Função genérica que exporta qualquer lista de dicionários para ficheiro CSV.

4. Funcionalidades – TP1 (API ItJobs):
4.1 Top N Ofertas (top)
Permite obter as N ofertas de emprego mais recentes. A visualização pode ser feita via JSON, Tabela formatada (--pretty) ou exportada para CSV.

4.2 Pesquisa Filtrada (search)
Realiza uma pesquisa de vagas aplicando filtros cumulativos:

Filtro por Empresa;

Filtro por Localidade;

Filtro de Negócio: Seleciona exclusivamente vagas do tipo "Part-time", conforme requisito do projeto.

4.3 Identificação do Regime (type)
Dado o ID de uma vaga, o sistema analisa o título e o corpo do anúncio utilizando Expressões Regulares para classificar o regime de trabalho em:

Remoto;

Híbrido;

Presencial/Outro.

4.4 Análise Temporal de Skills (skills):
Conta a frequência de tecnologias pré-definidas (Python, SQL, Java, etc.) nas descrições de vagas publicadas num intervalo de datas específico.

5. Funcionalidades – TP2 (Web Scraping):
5.1 Detalhe da Oferta Enriquecido (get)
Obtém os detalhes técnicos de uma vaga (via API) e cruza essa informação com o Teamlyzer (via Scraping) para adicionar:

Rating da empresa;

Descrição institucional;

Salários médios e Benefícios reportados.

5.2 Estatísticas por Zona (statistics)
Gera um relatório estatístico agregado, contabilizando o número de vagas por Zona Geográfica e Tipo de Contrato. O resultado é exportado automaticamente para o ficheiro estatisticas_zona.csv.

5.3 Top Skills no Teamlyzer (list-skills)
Acede à página de empregos do Teamlyzer para um cargo específico (ex: "Data Scientist") e extrai as tecnologias (tags) mais frequentes, permitindo identificar tendências de mercado.

6. Tratamento de Erros e Robustez:
O código foi desenvolvido com foco na estabilidade:

Utilização de blocos try-except para capturar falhas de rede ou erros na API.

Verificação da existência de dados antes de aceder a chaves de dicionários.

Feedback claro ao utilizador em caso de parâmetros inválidos ou falta de resultados.

7. Conclusão:
Este projeto cumpre todos os objetivos propostos, demonstrando a capacidade de integrar APIs REST com técnicas de Web Scraping para criar uma ferramenta de análise de dados funcional, modular e útil para a análise do mercado de trabalho em IT.




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