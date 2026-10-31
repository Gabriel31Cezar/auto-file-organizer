import json
from pathlib import Path
from typing import Dict, List, Set


class ConfigManager:
    """Gerenciador de configuracoes personalizadas e detector de pastas de projetos."""

    # Marcadores padrao que identificam uma pasta como sendo um projeto de desenvolvimento/trabalho
    DEFAULT_PROJECT_MARKERS: Set[str] = {
        ".git",
        ".gitignore",
        "package.json",
        "requirements.txt",
        "pom.xml",
        "build.gradle",
        "Cargo.toml",
        "pyproject.toml",
        "docker-compose.yml",
        ".vscode",
        ".idea",
    }

    # Matriz padrao de categorias e extensoes (v2.0.0)
    DEFAULT_CATEGORY_MAP: Dict[str, List[str]] = {
        "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".psd", ".ai", ".raw"],
        "Documentos": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".txt", ".csv", ".odt"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"],
        "Audios": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
        "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
        "Instaladores": [".exe", ".msi", ".bat", ".cmd"],
    }

    def __init__(self, config_path: Path | None = None):
        if config_path is None:
            self.config_path = Path(__file__).resolve().parent.parent / "config" / "user_config.json"
        else:
            self.config_path = Path(config_path)

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_data: Dict = {}
        self.load_config()

    def load_config(self) -> Dict:
        """Carrega as configuracoes salvas do arquivo JSON ou cria as configuracoes padrao."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config_data = json.load(f)
                    return self.config_data
            except Exception as e:
                print(f"Aviso: Nao foi possivel ler user_config.json ({e}). Usando padroes.")

        # Configuracao padrao caso o arquivo nao exista ou falhe
        self.config_data = {
            "protect_project_folders": True,
            "project_markers": list(self.DEFAULT_PROJECT_MARKERS),
            "category_map": self.DEFAULT_CATEGORY_MAP,
        }
        self.save_config()
        return self.config_data

    def save_config(self) -> None:
        """Salva as configuracoes atuais no disco em formato JSON."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)

    def is_project_directory(self, folder_path: Path) -> bool:
        """Verifica se um diretorio contem arquivos de marca de projeto (ex: .git, package.json)."""
        if not self.config_data.get("protect_project_folders", True):
            return False

        if not folder_path.exists() or not folder_path.is_dir():
            return False

        markers = set(self.config_data.get("project_markers", self.DEFAULT_PROJECT_MARKERS))

        # Verifica se algum marcador existe na pasta analisada
        for item in folder_path.iterdir():
            if item.name.lower() in {m.lower() for m in markers}:
                return True

        return False

    def get_category_map(self) -> Dict[str, List[str]]:
        """Retorna o dicionario ativo de categorias e extensoes."""
        return self.config_data.get("category_map", self.DEFAULT_CATEGORY_MAP)