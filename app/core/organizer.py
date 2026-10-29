import shutil
from pathlib import Path

# Dicionário que mapeia as categorias para as respetivas extensões de ficheiro
CATEGORY_MAP = {
    "Imagens": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp",
        ".svg",
        ".psd",
    ],
    "Documentos": [
        ".pdf",
        ".docx",
        ".doc",
        ".xlsx",
        ".xls",
        ".pptx",
        ".txt",
        ".csv",
    ],
    "Vídeos": [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"],
    "Áudios": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Instaladores": [".exe", ".msi"],
}


def get_unique_path(destination_dir: Path, filename: str) -> Path:
    """Garante que não sobrescrevemos um ficheiro existente.

    Se 'ficheiro.txt' já existir, gera 'ficheiro_1.txt', 'ficheiro_2.txt', etc.
    """
    destination = destination_dir / filename
    if not destination.exists():
        return destination

    stem = Path(filename).stem  # Nome do ficheiro sem a extensão
    suffix = Path(filename).suffix  # Extensão do ficheiro (ex: .pdf)
    counter = 1

    while destination.exists():
        new_name = f"{stem}_{counter}{suffix}"
        destination = destination_dir / new_name
        counter += 1

    return destination


def organize_directory(target_path: str) -> dict:
    """Lê a pasta selecionada e move os ficheiros para as subpastas correspondentes."""
    folder = Path(target_path)

    # Dicionário para contar quantos ficheiros foram movidos por categoria
    summary = {category: 0 for category in CATEGORY_MAP.keys()}
    summary["Outros"] = 0

    if not folder.exists() or not folder.is_dir():
        raise ValueError("O caminho especificado não é uma pasta válida.")

    for item in folder.iterdir():
        # Ignora se for uma pasta, ficheiro oculto ou temporário
        if (
            item.is_dir()
            or item.name.startswith(".")
            or item.suffix in [".tmp", ".crdownload"]
        ):
            continue

        file_ext = item.suffix.lower()
        category_found = None

        # Procura a categoria correspondente à extensão
        for category, extensions in CATEGORY_MAP.items():
            if file_ext in extensions:
                category_found = category
                break

        # Se não encontrar uma categoria conhecida, envia para 'Outros'
        if not category_found:
            category_found = "Outros"

        # Define e cria a subpasta da categoria
        category_dir = folder / category_found
        category_dir.mkdir(exist_ok=True)

        # Trata duplicados e move o ficheiro
        destination = get_unique_path(category_dir, item.name)
        shutil.move(str(item), str(destination))

        summary[category_found] += 1

    return summary