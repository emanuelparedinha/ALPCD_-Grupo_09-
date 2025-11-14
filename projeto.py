import typer
import csv
import re
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

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
    
    # --- A TUA CHAVE DE API FOI INSERIDA AQUI ---
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

# --- AQUI COMEÇA O TEU CÓDIGO (A, B, C) ---

def imprime_tabela_bonita(jobs_lista):
    """Função auxiliar para imprimir uma tabela formatada no terminal."""
    console = Console()
    table = Table(show_header=True, header_style="bold green", title="\nResultados (Formato Amigável)")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Título")
    table.add_column("Empresa")
    table.add_column("Localização")
    table.add_column("Data Publicação")

    for job in jobs_lista:
        empresa = job.get('company', {}).get('name', 'N/A')
        local = ', '.join(loc['name'] for loc in job.get('locations', []))
        data = job.get('publishedAt', 'N/A').split(' ')[0]

        table.add_row(
            str(job.get('id', 'N/A')),
            job.get('title', 'N/A'),
            empresa,
            local if local else 'N/A',
            data
        )
    
    console.print(table)


# --- Comandos da CLI ---

@app.command()
def top(
    n: int = typer.Argument(..., help="O número de trabalhos a listar."),
    csv_file: str = typer.Option(None, "--csv", help="Exportar o resultado para um ficheiro CSV."),
    pretty: bool = typer.Option(False, "--pretty", help="Mostrar também uma tabela formatada.")
):
    """
    (Alínea a) Lista os N trabalhos mais recentes publicados.
    """
    if n <= 0:
        typer.echo("O número de trabalhos (N) deve ser maior que 0.", err=True)
        raise typer.Exit()
        
    params = {"limit": n}
    response = request_api('list', params)

    if 'results' in response and response['results']:
        typer.echo(json.dumps(response['results'], indent=2))
        
        if pretty:
            imprime_tabela_bonita(response['results'])
        
        if csv_file:
            typer.echo(f"\n[Aviso: Função --csv (Alínea E) ainda não foi 'merged' pelo colega]")
            # cria_csv(response['results'], nome_arquivo=csv_file) # Esta linha vai dar erro até o merge
    else:
        typer.echo("Nenhum resultado encontrado.")

@app.command()
def search(
    localidade: str = typer.Argument(..., help="Localidade para filtrar."),
    empresa: str = typer.Argument(..., help="Nome da empresa para filtrar."),
    limit: int = typer.Argument(..., help="Número máximo de trabalhos a mostrar."),
    csv_file: str = typer.Option(None, "--csv", help="Exportar o resultado para um ficheiro CSV."),
    pretty: bool = typer.Option(False, "--pretty", help="Mostrar também uma tabela formatada.")
):
    """
    (Alínea b) Lista trabalhos (ex: Full-Time), por empresa e localidade.
    """
    if limit <= 0:
        typer.echo("O limite deve ser maior que 0.", err=True)
        raise typer.Exit()

    # ID '1' = Full-Time. Mudar para '2' se o requisito for Part-Time.
    params = {
        'limit': 1500,
        'type': '1' 
    }
    response = request_api('search', params)

    if 'results' in response and response['results']:
        trabalhos_filtrados = [
            trabalho for trabalho in response['results']
            if trabalho.get('company', {}).get('name', '').strip().lower() == empresa.strip().lower() and
            any(loc.get('name', '').strip().lower() == localidade.strip().lower() for loc in trabalho.get('locations', []))
        ]
        trabalhos_finais = trabalhos_filtrados[:limit]

        if trabalhos_finais:
            typer.echo(json.dumps(trabalhos_finais, indent=2))
            
            if pretty:
                imprime_tabela_bonita(trabalhos_finais)

            if csv_file:
                typer.echo(f"\n[Aviso: Função --csv (Alínea E) ainda não foi 'merged' pelo colega]")
                # cria_csv(trabalhos_finais, nome_arquivo=csv_file) # Esta linha vai dar erro até o merge
        else:
            typer.echo(f"Nenhum resultado encontrado para a empresa '{empresa}' na localidade '{localidade}'.")
    else:
        typer.echo("Nenhum resultado encontrado na API.")

@app.command()
def type(
    job_id: int = typer.Argument(..., help="O ID do trabalho a analisar.")
):
    """
    (Alínea c) Extrai o regime de trabalho (remoto/híbrido/presencial) de um job.
    """
    params = {"id": job_id}
    trabalho = request_api("get", params)

    if "error" in trabalho or not trabalho:
        typer.echo(f"Erro: A vaga com o ID {job_id} não foi encontrada.", err=True)
        raise typer.Exit()

    texto_para_analise = (
        trabalho.get('title', '') + " " +
        trabalho.get('body', '')
    ).lower() 

    soup = BeautifulSoup(texto_para_analise, 'lxml')
    texto_limpo = soup.get_text()

    if re.search(r"\b(h[íi]brido|hybrid)\b", texto_limpo):
        regime = "Híbrido"
    elif re.search(r"\b(remoto|remote|teletrabalho|work from home|wfh)\b", texto_limpo):
        regime = "Remoto"
    elif re.search(r"\b(presencial|on-site|escrit[óo]rio)\b", texto_limpo):
        regime = "Presencial"
    else:
        regime = "Outro (não especificado)"

    typer.echo(regime)


# --- FIM DOS COMANDOS ---

if __name__ == "__main__":
    app()