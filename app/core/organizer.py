import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config_manager import ConfigManager
from app.core.exif_reader import get_file_date
from app.core.history_logger import HistoryLogger


def get_unique_path(destination_dir: Path, filename: str) -> Path:
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


def _remove_empty_folders(root_folder: Path, reserved_categories: set) -> None:
    for path in sorted(root_folder.rglob("*"), reverse=True):
        if path.is_dir():
            try:
                relative_path = path.relative_to(root_folder)
                if relative_path.parts[0] in reserved_categories:
                    continue
                path.rmdir()
            except (OSError, ValueError, IndexError):
                pass


def organize_selected_files(
    target_path: str,
    selected_files: List[Dict[str, Any]],
    custom_folder_names: Optional[Dict[str, str]] = None,
    progress_callback=None
) -> Dict[str, int]:
    """Organiza apenas os arquivos expressamente selecionados pelo utilizador."""
    root_folder = Path(target_path).resolve()
    if not root_folder.exists() or not root_folder.is_dir():
        raise ValueError("O caminho especificado nao e uma pasta valida.")

    config = ConfigManager()
    category_map = config.get_category_map()

    if custom_folder_names is None:
        custom_folder_names = {cat: cat for cat in category_map.keys()}
        custom_folder_names["Outros"] = "Outros"

    logger = HistoryLogger()
    logger.start_session(str(root_folder))

    summary = {custom_folder_names.get(cat, cat): 0 for cat in category_map.keys()}
    summary["Outros"] = 0

    reserved_categories = set(custom_folder_names.values())
    total_files = len(selected_files)

    for index, file_info in enumerate(selected_files, start=1):
        item: Path = file_info["path"]
        if not item.exists():
            continue

        suggested_category = file_info["suggested_category"]
        custom_category_name = custom_folder_names.get(suggested_category, suggested_category)

        year, month_folder = get_file_date(item)
        category_dir = root_folder / custom_category_name / year / month_folder
        category_dir.mkdir(parents=True, exist_ok=True)

        destination = get_unique_path(category_dir, item.name)

        try:
            logger.log_move(item, destination)
            shutil.move(str(item), str(destination))
            summary[custom_category_name] = summary.get(custom_category_name, 0) + 1
        except Exception as e:
            print(f"Aviso: Nao foi possivel mover {item.name}. Motivo: {e}")

        if progress_callback:
            progress_callback(index, total_files)

    _remove_empty_folders(root_folder, reserved_categories)
    logger.save_session()

    return summary