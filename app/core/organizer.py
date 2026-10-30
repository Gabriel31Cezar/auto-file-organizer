import shutil
from pathlib import Path

# Importamos o extrator universal de datas
from app.core.exif_reader import get_file_date

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
        ".ai",
        ".raw",
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
        ".odt",
    ],
    "Vídeos": [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"],
    "Áudios": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Instaladores": [".exe", ".msi", ".bat", ".cmd"],
}


def get_unique_path(destination_dir: Path, filename: str) -> Path:
    """Garante a prevenção de duplicados sem sobrescrever ficheiros."""
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


def organize_directory(target_path: str, progress_callback=None) -> dict:
    """Realiza a organização recursiva completa de ficheiros por Categoria / Ano / Mês.

    Suporta callback de progresso para a interface gráfica.
    """
    root_folder = Path(target_path).resolve()

    if not root_folder.exists() or not root_folder.is_dir():
        raise ValueError("O caminho especificado não é uma pasta válida.")

    summary = {category: 0 for category in CATEGORY_MAP.keys()}
    summary["Outros"] = 0

    reserved_categories = set(CATEGORY_MAP.keys()) | {"Outros"}

    # Filtra os ficheiros elegíveis
    eligible_files = []
    for item in root_folder.rglob("*"):
        if not item.is_file():
            continue
        relative_path = item.relative_to(root_folder)
        if relative_path.parts[0] in reserved_categories:
            continue
        if item.name.startswith(".") or item.suffix.lower() in [".tmp", ".crdownload", ".part"]:
            continue
        eligible_files.append(item)

    total_files = len(eligible_files)

    for index, item in enumerate(eligible_files, start=1):
        file_ext = item.suffix.lower()
        category_found = None

        for category, extensions in CATEGORY_MAP.items():
            if file_ext in extensions:
                category_found = category
                break

        if not category_found:
            category_found = "Outros"

        # Extrai Ano e Mês para TODOS os tipos de ficheiros
        year, month_folder = get_file_date(item)

        # Estrutura padronizada: Categoria / Ano / Mês
        category_dir = root_folder / category_found / year / month_folder
        category_dir.mkdir(parents=True, exist_ok=True)

        destination = get_unique_path(category_dir, item.name)

        try:
            shutil.move(str(item), str(destination))
            summary[category_found] += 1
        except Exception as e:
            print(f"Aviso: Não foi possível mover {item.name}. Motivo: {e}")

        # Atualiza o progresso visual na interface gráfica
        if progress_callback:
            progress_callback(index, total_files)

    # Limpeza opcional de pastas vazias remanescentes
    _remove_empty_folders(root_folder, reserved_categories)

    return summary


def _remove_empty_folders(root_folder: Path, reserved_categories: set):
    """Remove subpastas que ficaram completamente vazias após a movimentação."""
    for folder in sorted(
        root_folder.rglob("*"), key=lambda p: len(p.parts), reverse=True
    ):
        if folder.is_dir() and folder.parts[-1] not in reserved_categories:
            try:
                # Remove apenas se a pasta estiver 100% vazia
                folder.rmdir()
            except OSError:
                pass