import typer
import csv
import re
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from rich.console import Console  # É bom ter os imports iguais
from rich.table import Table     # para evitar conflitos de merge fáceis.

# Headers para simular um navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

# Inicializa a aplicação Typer
app = typer.Typer()

def request_api(metodo, params):
    """
    Função central para fazer pedidos à API itjobs.pt.
    Já trata da API key e da paginação.
    """
    url = "https://api.itjobs.pt/job"
    
    # --- A CHAVE DE API DEVE SER INSERIDA AQUI ---
    api_key = "ace3b0c8f977143fe22f7f75dab01463"
    
    params['api_key'] = api_key

    # Lógica de paginação
    if 'limit' in params and metodo != 'get':
        tamanho_pagina = 500
        total = params['limit']
        if total < tamanho_pagina:
            tamanho_pagina = total

        paginas_totais = (total // tamanho_pagina) + (1 if total % tamanho_pagina != 0 else 0)
        resultado = []

        for page in range(1, paginas_totais + 1):
            params_pagina = params.copy()
            params_pagina['limit'] = tamanho_pagina
            params_pagina['page'] = page

            try:
                response = requests.get(f"{url}/{metodo}.json", headers=headers, params=params_pagina, timeout=10)
                response.raise_for_status() 
            except requests.RequestException as e:
                typer.echo(f"Erro ao acessar a API: {e}", err=True)
                return {}

            if response.status_code == 200:
                response_data = response.json()
                if 'results' in response_data:
                    resultado.extend(response_data['results'])
                if len(resultado) >= total:
                    resultado = resultado[:total]
                    break
                if len(response_data.get('results', [])) < tamanho_pagina:
                    break
            else:
                typer.echo(f"Erro ao acessar a API: {response.status_code}", err=True)
                return {}
        return {"results": resultado}
    else:
        # Pedido simples (ex: get por ID)
        try:
            response = requests.get(f"{url}/{metodo}.json", headers=headers, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            typer.echo(f"Erro ao acessar a API: {e}", err=True)
            return {}

        if response.status_code == 200:
            return response.json()
        else:
            typer.echo(f"Erro ao acessar a API: {response.status_code}", err=True)
            return {}

# --- AQUI COMEÇA O CÓDIGO DO COLEGA (D, E) ---

def cria_csv(dados, nome_arquivo='trabalhos.csv', colunas_override=None):
    """
    (Alínea e)
    Função para criar o CSV. 
    Se 'colunas_override' for None, usa o formato padrão (para alíneas a, b).
    Se for uma lista, usa essa lista (para a alínea d).
    """
    
    if colunas_override:
        colunas_finais = colunas_override
        # Para a alínea D, os 'dados' já são uma lista de dicts prontos
        dados_para_escrever = dados
    else:
        # Modo Padrão (para alíneas a, b, quando for feito o merge)
        colunas_finais = ['id', 'titulo', 'empresa', 'descrição', 'data de publicação', 'salário', 'localização', 'url']
        dados_para_escrever = []
        for trabalho in dados:
            body_html = trabalho.get('body', '')
            if body_html:
                soup_limpeza = BeautifulSoup(body_html, "lxml")
                texto_sujo = soup_limpeza.get_text(separator=" ")
                descricao_limpa = re.sub(r'\s+', ' ', texto_sujo).strip()
            else:
                descricao_limpa = 'N/A'
            
            dados_para_escrever.append({
                'id': trabalho.get('id', 'N/A'),
                'titulo': trabalho.get('title', 'N/A'),
                'empresa': trabalho.get('company', {}).get('name', 'N/A'),
                'descrição': descricao_limpa,
                'data de publicação': trabalho.get('publishedAt', 'N/A'),
                'salário': trabalho.get('wage', 'N/A'),
                'localização': ', '.join(loc['name'] for loc in trabalho.get('locations', [])),
                'url': trabalho.get('url', 'N/A')
            })

    try:
        with open(nome_arquivo, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=colunas_finais, delimiter=';')
            writer.writeheader()
            writer.writerows(dados_para_escrever)
        typer.echo(f"\nDados exportados para {nome_arquivo}")
    except IOError as e:
        typer.echo(f"Erro ao escrever o ficheiro CSV: {e}", err=True)


# --- Comandos da CLI ---

@app.command()
def skills(
    data_inicial: str = typer.Argument(..., help="Data inicial (YYYY-MM-DD)."),
    data_final: str = typer.Argument(..., help="Data final (YYYY-MM-DD)."),
    csv_file: str = typer.Option(None, "--csv", help="Exportar o resultado para um ficheiro CSV.")
):
    """
    (Alínea d) Conta ocorrências de skills nas descrições entre duas datas.
    """
    # Lista de skills a procurar
    SKILLS_LIST = [
        "python", "java", "javascript", "react", "angular", "vue", 
        "sql", "nosql", "mongodb", "postgres", "c#", ".net", "php", 
        "laravel", "aws", "azure", "gcp", "docker", "kubernetes", "go"
    ]
    
    try:
        data_inicial_dt = datetime.strptime(data_inicial, "%Y-%m-%d").date()
        data_final_dt = datetime.strptime(data_final, "%Y-%m-%d").date()
    except ValueError:
        typer.echo("Erro: As datas devem estar no formato 'YYYY-MM-DD'.", err=True)
        raise typer.Exit()

    if data_inicial_dt > data_final_dt:
        typer.echo("Erro: A data inicial não pode ser posterior à data final.", err=True)
        raise typer.Exit()

    skill_counts = {skill: 0 for skill in SKILLS_LIST}
    
    params = {"limit": 1500} # Limite alto
    typer.echo("A contactar a API... Isto pode demorar um pouco.")
    trabalhos = request_api("search", params)

    if not trabalhos or "results" not in trabalhos:
        typer.echo("Nenhum resultado encontrado ou erro na API.", err=True)
        raise typer.Exit()
    
    trabalhos_no_periodo = 0
    typer.echo(f"A processar {len(trabalhos['results'])} trabalhos...")
    
    for trabalho in trabalhos["results"]:
        try:
            data_publicacao_dt = datetime.strptime(trabalho["publishedAt"], "%Y-%m-%d %H:%M:%S").date()
        except (ValueError, TypeError, KeyError):
            continue 

        if data_inicial_dt <= data_publicacao_dt <= data_final_dt:
            trabalhos_no_periodo += 1
            descricao = (trabalho.get('body', '') + " " + trabalho.get('title', '')).lower()
            
            for skill in SKILLS_LIST:
                if re.search(rf"\b{re.escape(skill)}\b", descricao):
                    skill_counts[skill] += 1

    # Ordena por contagem
    contagens_ordenadas = dict(
        sorted(skill_counts.items(), key=lambda item: item[1], reverse=True)
    )
    
    # Filtra skills com contagem > 0
    contagens_finais = {k: v for k, v in contagens_ordenadas.items() if v > 0}
    
    # Formato JSON pedido no PDF
    output_json = [contagens_finais]

    typer.echo(f"Analisados {trabalhos_no_periodo} trabalhos encontrados entre {data_inicial} e {data_final}.")
    typer.echo(json.dumps(output_json, indent=2))
    
    # (Alínea E)
    if csv_file:
        # Prepara dados para o CSV
        dados_csv = [{"skill": k, "contagem": v} for k, v in contagens_finais.items()]
        # Chama a função cria_csv com colunas personalizadas
        cria_csv(dados_csv, nome_arquivo=csv_file, colunas_override=["skill", "contagem"])


# --- FIM DOS COMANDOS ---

if __name__ == "__main__":
    app()