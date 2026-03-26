"""
╔══════════════════════════════════════════════════════════╗
║              📸 Pexels Bulk Downloader                   ║
║         Baixe fotos da Pexels em massa via CLI           ║
╚══════════════════════════════════════════════════════════╝

Dependências:
    pip install requests rich

Uso:
    python pexels_cli.py                → Menu interativo
    python pexels_cli.py config         → Configurar API key
    python pexels_cli.py download       → Download interativo
    python pexels_cli.py download -q "dog, cat, bird"
    python pexels_cli.py download -q "dog, cat" -n 5 -o fotos -s large --landscape
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Módulo 'requests' não encontrado. Rode: pip install requests")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        MofNCompleteColumn,
        TimeElapsedColumn,
    )
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.text import Text
    from rich.rule import Rule
    from rich import box
except ImportError:
    print("❌ Módulo 'rich' não encontrado. Rode: pip install rich")
    sys.exit(1)


# ── Globals ──────────────────────────────────────────────

console = Console()
CONFIG_FILE = Path(__file__).parent / ".pexels_config.json"
API_BASE = "https://api.pexels.com/v1/search"

VALID_SIZES = ["original", "large2x", "large", "medium", "small", "tiny"]
VALID_ORIENTATIONS = ["portrait", "landscape", "square"]

BANNER = r"""
[bold cyan]
    ____               __        ____  __    __
   / __ \___  _  _____/ /____   / __ \/ /   / /
  / /_/ / _ \| |/_/ _ \/ / ___/ / / / / /   / / 
 / ____/  __/>  </  __/ (__  ) / /_/ / /___/ /  
/_/    \___/_/|_|\___/_/____/  \____/_____/_/   
[/bold cyan]
[dim]Bulk Photo Downloader · Pexels API[/dim]
"""


# ── Config Management ────────────────────────────────────


def load_config() -> dict:
    """Carrega configuração do arquivo JSON."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_config(config: dict):
    """Salva configuração no arquivo JSON."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key() -> str | None:
    """Retorna a API key salva ou None."""
    config = load_config()
    return config.get("api_key")


def set_api_key(key: str):
    """Salva a API key no arquivo de config."""
    config = load_config()
    config["api_key"] = key
    save_config(config)


def validate_api_key(key: str) -> bool:
    """Testa se a API key é válida fazendo uma busca simples."""
    try:
        resp = requests.get(
            API_BASE,
            headers={"Authorization": key},
            params={"query": "test", "per_page": 1},
            timeout=10,
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False


# ── API ──────────────────────────────────────────────────


def search_photos(
    api_key: str,
    query: str,
    per_page: int = 3,
    orientation: str = "portrait",
) -> list:
    """Busca fotos na Pexels API."""
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation,
    }
    resp = requests.get(API_BASE, headers=headers, params=params, timeout=15)
    if resp.status_code == 200:
        return resp.json().get("photos", [])
    return []


def download_file(url: str, filepath: Path) -> bool:
    """Baixa um arquivo para o disco."""
    try:
        resp = requests.get(url, stream=True, timeout=30)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return True
    except requests.RequestException:
        pass
    return False


# ── Slug helper ──────────────────────────────────────────


def slugify(text: str) -> str:
    """Transforma texto em slug para nome de pasta."""
    slug = text.strip().lower()
    slug = slug.replace(" ", "_").replace("-", "_")
    safe = "".join(c for c in slug if c.isalnum() or c == "_")
    # colapsa underscores duplos
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_")[:60]


# ── CLI Commands ─────────────────────────────────────────


def cmd_config():
    """Comando: configurar API key."""
    console.print(BANNER)
    console.print(Rule("[bold yellow]⚙️  Configuração[/bold yellow]"))

    current = get_api_key()
    if current:
        masked = current[:8] + "•" * (len(current) - 12) + current[-4:]
        console.print(f"\n  Key atual: [dim]{masked}[/dim]")
        if not Confirm.ask("\n  Deseja trocar a API key?", default=False):
            return

    console.print(
        "\n  [dim]Pegue sua key grátis em:[/dim] [bold link=https://www.pexels.com/api/]https://www.pexels.com/api/[/bold link]\n"
    )

    key = Prompt.ask("  Cole sua API key").strip()

    if not key:
        console.print("  [red]Key vazia, cancelando.[/red]")
        return

    console.print("  [dim]Validando key...[/dim]", end=" ")
    if validate_api_key(key):
        set_api_key(key)
        console.print("[bold green]✓ Key válida e salva![/bold green]")
        console.print(f"  [dim]Salva em: {CONFIG_FILE}[/dim]")
    else:
        console.print("[bold red]✗ Key inválida ou sem conexão.[/bold red]")


def cmd_download(
    queries_str: str | None = None,
    num_photos: int | None = None,
    output_dir: str | None = None,
    size: str | None = None,
    orientation: str | None = None,
):
    """Comando: baixar fotos."""
    console.print(BANNER)
    console.print(Rule("[bold green]📥 Download[/bold green]"))

    # ── Checa API key ──
    api_key = get_api_key()
    if not api_key:
        console.print(
            "\n  [red]Nenhuma API key configurada![/red]"
            "\n  Rode: [bold]python pexels_cli.py config[/bold]\n"
        )
        return

    # ── Queries ──
    if not queries_str:
        console.print(
            "\n  Digite os termos de busca separados por [bold]vírgula[/bold]."
        )
        console.print(
            '  [dim]Ex: person scrolling phone, confused person thinking, robot and human[/dim]\n'
        )
        queries_str = Prompt.ask("  🔍 Termos de busca")

    queries = [q.strip() for q in queries_str.split(",") if q.strip()]

    if not queries:
        console.print("  [red]Nenhum termo informado, cancelando.[/red]")
        return

    # ── Parâmetros ──
    if num_photos is None:
        num_photos = IntPrompt.ask(
            "  📸 Fotos por termo", default=3, show_default=True
        )

    if orientation is None:
        console.print(
            "\n  Orientação: [bold]portrait[/bold] (vertical/TikTok), landscape, square"
        )
        orientation = Prompt.ask(
            "  📐 Orientação",
            default="portrait",
            show_default=True,
        )

    if orientation not in VALID_ORIENTATIONS:
        console.print(f"  [yellow]Orientação '{orientation}' inválida, usando 'portrait'[/yellow]")
        orientation = "portrait"

    if size is None:
        size = Prompt.ask(
            "  📏 Tamanho (original/large2x/large/medium/small)",
            default="large",
            show_default=True,
        )

    if size not in VALID_SIZES:
        console.print(f"  [yellow]Tamanho '{size}' inválido, usando 'large'[/yellow]")
        size = "large"

    if output_dir is None:
        output_dir = Prompt.ask(
            "  📁 Pasta de saída", default="pexels_photos", show_default=True
        )

    # ── Resumo ──
    console.print()
    summary = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    summary.add_column(style="bold cyan")
    summary.add_column()
    summary.add_row("Termos", str(len(queries)))
    summary.add_row("Fotos/termo", str(num_photos))
    summary.add_row("Total estimado", f"~{len(queries) * num_photos} fotos")
    summary.add_row("Orientação", orientation)
    summary.add_row("Tamanho", size)
    summary.add_row("Pasta", output_dir)
    console.print(Panel(summary, title="[bold]Resumo[/bold]", border_style="cyan"))

    if not Confirm.ask("\n  Iniciar download?", default=True):
        console.print("  [dim]Cancelado.[/dim]")
        return

    # ── Download ──
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    total_downloaded = 0
    total_skipped = 0
    total_errors = 0
    results_log: list[dict] = []

    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        main_task = progress.add_task("Download total", total=len(queries))

        for query in queries:
            slug = slugify(query)
            scene_dir = out_path / slug
            scene_dir.mkdir(exist_ok=True)

            progress.update(
                main_task,
                description=f"[cyan]🔍 {query[:40]}...[/cyan]"
                if len(query) > 40
                else f"[cyan]🔍 {query}[/cyan]",
            )

            photos = search_photos(api_key, query, num_photos, orientation)

            scene_downloaded = 0

            if not photos:
                results_log.append(
                    {"query": query, "status": "⚠️  Sem resultados", "count": 0}
                )
                progress.advance(main_task)
                continue

            for j, photo in enumerate(photos, 1):
                photo_url = photo["src"].get(size, photo["src"]["large"])
                photographer = slugify(photo.get("photographer", "unknown"))[:20]
                filename = f"{slug}_{j}_{photographer}.jpg"
                filepath = scene_dir / filename

                if filepath.exists():
                    total_skipped += 1
                    continue

                if download_file(photo_url, filepath):
                    total_downloaded += 1
                    scene_downloaded += 1
                else:
                    total_errors += 1

            results_log.append(
                {
                    "query": query,
                    "status": "✅ OK" if scene_downloaded > 0 else "⏭️  Cache",
                    "count": scene_downloaded,
                }
            )

            progress.advance(main_task)
            time.sleep(0.3)  # rate limit

    # ── Relatório final ──
    console.print()
    console.print(Rule("[bold]📊 Resultado[/bold]"))

    table = Table(box=box.SIMPLE_HEAVY, padding=(0, 1))
    table.add_column("#", style="dim", width=4)
    table.add_column("Termo de busca", min_width=30)
    table.add_column("Status", width=16)
    table.add_column("Baixadas", justify="right", width=10)

    for i, row in enumerate(results_log, 1):
        table.add_row(
            str(i),
            row["query"],
            row["status"],
            str(row["count"]),
        )

    console.print(table)

    # Stats
    console.print()
    stats = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    stats.add_column(style="bold")
    stats.add_column(justify="right")
    stats.add_row("[green]✅ Baixadas[/green]", str(total_downloaded))
    stats.add_row("[yellow]⏭️  Já existiam[/yellow]", str(total_skipped))
    stats.add_row("[red]❌ Erros[/red]", str(total_errors))
    stats.add_row("[cyan]📁 Pasta[/cyan]", str(out_path.resolve()))
    console.print(Panel(stats, title="[bold]Resumo Final[/bold]", border_style="green"))
    console.print()


def cmd_menu():
    """Menu interativo principal."""
    console.print(BANNER)

    api_key = get_api_key()
    status = "[bold green]✓ Configurada[/bold green]" if api_key else "[bold red]✗ Não configurada[/bold red]"
    console.print(f"  API Key: {status}\n")

    console.print("  [bold cyan]1[/bold cyan] · ⚙️  Configurar API key")
    console.print("  [bold cyan]2[/bold cyan] · 📥 Baixar fotos")
    console.print("  [bold cyan]3[/bold cyan] · 🚪 Sair")
    console.print()

    choice = Prompt.ask("  Escolha", choices=["1", "2", "3"], default="2")

    if choice == "1":
        console.print()
        cmd_config()
    elif choice == "2":
        console.print()
        cmd_download()
    else:
        console.print("  [dim]Até mais! 👋[/dim]")


# ── Argument Parser ──────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="📸 Pexels Bulk Photo Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python pexels_cli.py                              Menu interativo
  python pexels_cli.py config                       Configurar API key
  python pexels_cli.py download                     Download interativo
  python pexels_cli.py download -q "dog, cat, bird"
  python pexels_cli.py download -q "dog, cat" -n 5 -o fotos -s large --portrait
        """,
    )

    sub = parser.add_subparsers(dest="command")

    # config
    sub.add_parser("config", help="Configurar API key")

    # download
    dl = sub.add_parser("download", help="Baixar fotos")
    dl.add_argument("-q", "--queries", type=str, help='Termos separados por vírgula: "dog, cat, bird"')
    dl.add_argument("-n", "--num", type=int, help="Fotos por termo (padrão: 3)")
    dl.add_argument("-o", "--output", type=str, help="Pasta de saída (padrão: pexels_photos)")
    dl.add_argument("-s", "--size", type=str, choices=VALID_SIZES, help="Tamanho da foto")
    dl.add_argument("--portrait", action="store_const", const="portrait", dest="orientation", help="Orientação vertical (TikTok)")
    dl.add_argument("--landscape", action="store_const", const="landscape", dest="orientation", help="Orientação horizontal")
    dl.add_argument("--square", action="store_const", const="square", dest="orientation", help="Orientação quadrada")

    return parser


# ── Main ─────────────────────────────────────────────────


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "config":
        cmd_config()
    elif args.command == "download":
        cmd_download(
            queries_str=args.queries,
            num_photos=args.num,
            output_dir=args.output,
            size=args.size,
            orientation=args.orientation,
        )
    else:
        cmd_menu()


if __name__ == "__main__":
    main()
