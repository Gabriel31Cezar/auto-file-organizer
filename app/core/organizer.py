import shutil
from pathlib import Path

# Importamos o leitor de datas que criámos no módulo ao lado
from app.core.exif_reader import get_photo_date

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
    """Garante que não sobrescrevemos um ficheiro existente."""
    destination = destination_dir / filename
    if not destination.exists():
        return destination

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1

    while destination.exists():
        new_name = f"{stem}_{counter}{suffix}"
        destination = destination_dir / new_name
        counter += 1

    return destination


def organize_directory(target_path: str) -> dict:
    """Lê a pasta selecionada e move os ficheiros para as subpastas correspondentes,

    organizando imagens por Ano e Mês.
    """
    folder = Path(target_path)

    summary = {category: 0 for category in CATEGORY_MAP.keys()}
    summary["Outros"] = 0

    if not folder.exists() or not folder.is_dir():
        raise ValueError("O caminho especificado não é uma pasta válida.")

    for item in folder.iterdir():
        if (
            item.is_dir()
            or item.name.startswith(".")
            or item.suffix in [".tmp", ".crdownload"]
        ):
            continue

        file_ext = item.suffix.lower()
        category_found = None

        for category, extensions in CATEGORY_MAP.items():
            if file_ext in extensions:
                category_found = category
                break

        if not category_found:
            category_found = "Outros"

        # Lógica especial para Imagens: organiza por Ano e Mês
        if category_found == "Imagens":
            year, month_folder = get_photo_date(item)
            category_dir = folder / "Imagens" / year / month_folder
        else:
            category_dir = folder / category_found

        # Cria a estrutura de pastas necessária
        category_dir.mkdir(parents=True, exist_ok=True)

        # Trata duplicados e move o ficheiro
        destination = get_unique_path(category_dir, item.name)
        shutil.move(str(item), str(destination))

        summary[category_found] += 1

    return summary