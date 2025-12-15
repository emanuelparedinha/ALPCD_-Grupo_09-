import typer
import csv
import re
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

# --- CONFIGURAÇÕES GLOBAIS ---
app = typer.Typer(help="CLI para TP1 e TP2 (Alíneas A e B)")
console = Console()

HEADERS_GENERIC = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
HEADERS_TEAMLYZER = {
    "User-Agent": "Mozilla/5.0 (compatible; TeamlyzerScraper/1.0)"
}

ITJOBS_API_KEY = "ace3b0c8f977143fe22f7f75dab01463"
ITJOBS_URL = "https://api.itjobs.pt/job"

# --- FUNÇÕES AUXILIARES (Base para ambos) ---

def request_api(metodo, params):
    """Função central para pedidos à API itjobs.pt com paginação."""
    params['api_key'] = ITJOBS_API_KEY
    if metodo == 'get':
        try:
            res = requests.get(f"{ITJOBS_URL}/get.json", headers=HEADERS_GENERIC, params=params, timeout=15)
            res.raise_for_status()
            return res.json()
        except Exception: return {}

    limit = params.get('limit', 100)
    page_size = 500 if limit > 500 else limit
    results = []
    page = 1
    
    while len(results) < limit:
        p_req = params.copy()
        p_req['limit'] = page_size
        p_req['page'] = page
        try:
            res = requests.get(f"{ITJOBS_URL}/{metodo}.json", headers=HEADERS_GENERIC, params=p_req, timeout=15)
            if res.status_code != 200: break
            data = res.json()
            if not data.get('results'): break
            results.extend(data['results'])
            page += 1
        except: break
    return {"results": results[:limit]}

def get_soup_teamlyzer(url):
    """[TP2] Helper para scraping do Teamlyzer."""
    try:
        res = requests.get(url, headers=HEADERS_TEAMLYZER, timeout=10)
        if res.status_code == 200: return BeautifulSoup(res.text, "html.parser")
    except: pass
    return None

def limpar_texto_html(html_content):
    """Limpa HTML e espaços."""
    if not html_content: return "N/A"
    soup = BeautifulSoup(str(html_content), "html.parser")
    return re.sub(r'\s+', ' ', soup.get_text(separator=" ")).strip()

def imprime_tabela_bonita(jobs_lista):
    """Imprime tabela formatada."""
    table = Table(show_header=True, header_style="bold green")
    table.add_column("ID", width=8); table.add_column("Título"); table.add_column("Empresa")
    for j in jobs_lista:
        table.add_row(str(j.get('id')), j.get('title')[:40], j.get('company', {}).get('name', 'N/A')[:25])
    console.print(table)

def cria_csv(dados, nome_arquivo, colunas=None):
    """Gera CSV (TP1-e / TP2-d)."""
    if not dados: return
    if not colunas: colunas = list(dados[0].keys())
    try:
        with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=colunas, extrasaction='ignore') 
            writer.writeheader()
            writer.writerows(dados)
        typer.secho(f"CSV criado: {nome_arquivo}", fg=typer.colors.GREEN)
    except Exception as e: typer.echo(f"Erro CSV: {e}")

# --- COMANDOS TP 1 (Completo) ---

@app.command()
def top(n: int = typer.Argument(...), csv_file: str = typer.Option(None, "--csv"), pretty: bool = False):
    """(TP1-a) Top N trabalhos."""
    res = request_api('list', {'limit': n})
    jobs = res.get('results', [])
    typer.echo(json.dumps(jobs, indent=2))
    if pretty: imprime_tabela_bonita(jobs)
    if csv_file:
        flat_jobs = [{"titulo": j.get('title'), "empresa": j.get('company', {}).get('name'), "data": j.get('publishedAt')} for j in jobs]
        cria_csv(flat_jobs, csv_file)

@app.command()
def search(localidade: str, empresa: str, limit: int, csv_file: str = typer.Option(None, "--csv"), pretty: bool = False):
    """(TP1-b) Pesquisa Part-time."""
    res = request_api('search', {'limit': 2000})
    filtrados = [j for j in res.get('results', []) 
                 if empresa.lower() in j.get('company', {}).get('name', '').lower() 
                 and any(localidade.lower() in l.get('name', '').lower() for l in j.get('locations', []))
                 and any('part-time' in t.get('name', '').lower() for t in j.get('types', []))] # Filtro Part-time
    
    finais = filtrados[:limit]
    typer.echo(json.dumps(finais, indent=2))
    if pretty: imprime_tabela_bonita(finais)
    if csv_file:
        flat_jobs = [{"titulo": j.get('title'), "empresa": j.get('company', {}).get('name')} for j in finais]
        cria_csv(flat_jobs, csv_file)

@app.command(name="type")
def job_type(job_id: int):
    """(TP1-c) Regime (Remoto/Híbrido)."""
    res = request_api('get', {'id': job_id})
    if 'title' not in res: return typer.echo("Job não encontrado.")
    txt = limpar_texto_html(res.get('title', '') + " " + res.get('body', '')).lower()
    if re.search(r"\b(h[íi]brido|hybrid)\b", txt): typer.echo("Híbrido")
    elif re.search(r"\b(remoto|remote|teletrabalho)\b", txt): typer.echo("Remoto")
    else: typer.echo("Presencial/Outro")

@app.command()
def skills(d_ini: str, d_fim: str, csv_file: str = typer.Option(None, "--csv")):
    """(TP1-d) Contar skills."""
    SKILLS = ["python", "java", "sql", "react", "javascript", "docker"]
    try: date_i, date_f = datetime.strptime(d_ini, "%Y-%m-%d"), datetime.strptime(d_fim, "%Y-%m-%d")
    except: return typer.echo("Datas inválidas.")
    
    counts = {s: 0 for s in SKILLS}
    res = request_api('search', {'limit': 1000})
    for j in res.get('results', []):
        try: 
            p_date = datetime.strptime(j.get('publishedAt', '').split()[0], "%Y-%m-%d")
            if date_i <= p_date <= date_f:
                desc = limpar_texto_html(j.get('body', '') + " " + j.get('title', '')).lower()
                for s in SKILLS: 
                    if re.search(rf"\b{re.escape(s)}\b", desc): counts[s] += 1
        except: continue
    
    res_final = {k: v for k,v in sorted(counts.items(), key=lambda x:x[1], reverse=True) if v > 0}
    typer.echo(json.dumps([res_final], indent=2))
    if csv_file: cria_csv([{"Skill": k, "Count": v} for k,v in res_final.items()], csv_file)

# --- COMANDOS TP 2 (Alíneas A e B - TUA PARTE) ---

@app.command()
def get(job_id: int, csv_file: str = typer.Option(None, "--csv")):
    """(TP2-a) Detalhe + Teamlyzer Scrape."""
    res = request_api('get', {'id': job_id})
    if not res or 'title' not in res: return typer.echo("Job não encontrado.")

    empresa = res.get('company', {}).get('name')
    extras = {"teamlyzer_rating": "N/A", "teamlyzer_desc": "N/A", "teamlyzer_salary": "N/A", "teamlyzer_benefits": "N/A"}
    
    if empresa:
        slug = empresa.lower().strip().replace(" ", "-").replace(".", "")
        soup = get_soup_teamlyzer(f"https://pt.teamlyzer.com/companies/{slug}")
        if soup:
            rt = soup.find("span", class_="rating-value")
            if rt: extras["teamlyzer_rating"] = limpar_texto_html(rt.text)
            desc = soup.find("div", class_="company-bio")
            if desc: extras["teamlyzer_desc"] = limpar_texto_html(desc.text)
            # Salário e Benefícios
            for el in soup.find_all(["h3", "strong", "h4"]):
                if "Salário" in el.get_text(): 
                    prox = el.find_next() 
                    if prox: extras["teamlyzer_salary"] = limpar_texto_html(prox.text)
                if "Benefícios" in el.get_text():
                    ul = el.find_next("ul")
                    if ul: extras["teamlyzer_benefits"] = "; ".join([li.get_text(strip=True) for li in ul.find_all("li")])

    res.update(extras)
    typer.echo(json.dumps(res, indent=4, ensure_ascii=False))
    
    if csv_file: 
        flat = res.copy()
        flat['company'] = empresa
        flat['location'] = ", ".join([l.get('name', '') for l in flat.get('locations', [])])
        flat['body'] = limpar_texto_html(flat.get('body'))
        cria_csv([flat], csv_file, ["id", "title", "company", "teamlyzer_rating", "teamlyzer_salary", "teamlyzer_benefits"])

@app.command()
def statistics(zone: str = typer.Argument(None)):
    """(TP2-b) Estatísticas Zona/Tipo."""   # <--- A LINHA CORRIGIDA É ESTA
    typer.echo("Calculando estatísticas...")
    res = request_api('search', {'limit': 1500})
    stats = {}
    
    for j in res.get('results', []):
        t_nome = j.get('types', [])[0].get('name', 'N/A') if j.get('types') else 'N/A'
        for loc in j.get('locations', []):
            z_nome = loc.get('name', 'N/A')
            if zone and zone.lower() not in z_nome.lower(): continue
            k = (z_nome, t_nome)
            stats[k] = stats.get(k, 0) + 1
            
    lista = [{"Zona": z, "Tipo de Trabalho": t, "Nº de vagas": c} for (z, t), c in sorted(stats.items())]
    cria_csv(lista, "estatisticas_zona.csv", ["Zona", "Tipo de Trabalho", "Nº de vagas"]) 
    typer.echo("CSV 'estatisticas_zona.csv' criado.")

if __name__ == "__main__":
    app()