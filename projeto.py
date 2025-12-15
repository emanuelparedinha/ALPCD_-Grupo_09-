--- COMANDO TP 2 (Alínea C e D - PARTE DO COLEGA) ---,
@app.command(name="list-skills")
def list_skills_tp2(job_title: str, csv_file: str = typer.Option(None, "--csv")):
    [cite_start]"""(TP2-c) Top Skills Teamlyzer[cite: 143]."""
    tag = job_title.lower().replace(" ", "+")
    url = f"https://pt.teamlyzer.com/companies/jobs?tags={tag}&order=most_relevant"
    typer.echo(f"Analisando: {url}")

    soup = get_soup_teamlyzer(url)
    if not soup: return typer.echo("Erro ao aceder ao Teamlyzer.")

    cnt = {}
    for a in soup.find_all("a", href=re.compile(r"tags=")):
        s = limpar_texto_html(a.text).lower()
        if s and s != job_title.lower() and len(s) < 30:
            cnt[s] = cnt.get(s, 0) + 1

    top = [{"skill": k, "count": v} for k, v in sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:10]]
    typer.echo(json.dumps(top, indent=2))

    [cite_start]if csv_file: # (TP2-d aplicado à alínea c) [cite: 149]
        cria_csv(top, csv_file, ["skill", "count"])