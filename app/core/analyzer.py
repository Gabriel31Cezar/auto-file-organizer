from pathlib import Path
from typing import Dict, List, Any
from app.core.config_manager import ConfigManager


class DirectoryAnalyzer:
    """Realiza a analise previa (Dry-Run / Preview) e lista todos os arquivos para selecao."""

    def __init__(self, config_manager: ConfigManager | None = None):
        self.config = config_manager if config_manager else ConfigManager()

    def analyze_directory(self, target_path: str) -> Dict[str, Any]:
        """Varre o diretorio alvo recursivamente e mapeia todos os arquivos."""
        root_folder = Path(target_path).resolve()
        if not root_folder.exists() or not root_folder.is_dir():
            raise ValueError("O caminho especificado nao e uma pasta valida.")

        category_map = self.config.get_category_map()
        reserved_categories = set(category_map.keys()) | {"Outros"}

        eligible_files_list: List[Dict[str, Any]] = []
        ignored_project_files_count = 0
        ignored_system_files_count = 0
        project_folders_detected: List[str] = []

        for item in root_folder.rglob("*"):
            if item.is_dir():
                if self.config.is_project_directory(item):
                    rel_path = str(item.relative_to(root_folder))
                    if rel_path not in project_folders_detected:
                        project_folders_detected.append(rel_path)
                continue

            relative_path = item.relative_to(root_folder)

            if relative_path.parts[0] in reserved_categories:
                continue

            parent_is_project = False
            for parent in item.parents:
                if parent == root_folder:
                    break
                if self.config.is_project_directory(parent):
                    parent_is_project = True
                    break

            if parent_is_project:
                ignored_project_files_count += 1
                continue

            if item.name.startswith(".") or item.suffix.lower() in [".tmp", ".crdownload", ".part"]:
                ignored_system_files_count += 1
                continue

            file_ext = item.suffix.lower() if item.suffix else ".sem_extensao"
            category_found = "Outros"
            for category, extensions in category_map.items():
                if file_ext in extensions:
                    category_found = category
                    break

            eligible_files_list.append({
                "path": item,
                "name": item.name,
                "relative_path": str(relative_path),
                "extension": file_ext,
                "suggested_category": category_found
            })

        return {
            "target_path": str(root_folder),
            "files": eligible_files_list,
            "ignored_project_files_count": ignored_project_files_count,
            "ignored_system_files_count": ignored_system_files_count,
            "project_folders_detected": project_folders_detected,
        }