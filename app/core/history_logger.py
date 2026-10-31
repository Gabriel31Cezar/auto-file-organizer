import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class HistoryLogger:
    """Gerenciador de logs transacionais e motor de reversão (Undo) para o Auto File Organizer."""

    def __init__(self, log_dir: Optional[Path] = None):
        if log_dir is None:
            self.log_dir = Path(__file__).resolve().parent.parent / "logs"
        else:
            self.log_dir = Path(log_dir)

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_files: List[Dict[str, str]] = []
        self.current_session_id: str = ""
        self.target_directory: str = ""

    def start_session(self, target_directory: str) -> str:
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.target_directory = target_directory
        self.current_session_files = []
        return self.current_session_id

    def log_move(self, original_path: Path, new_path: Path) -> None:
        self.current_session_files.append({
            "original_path": str(original_path.resolve()),
            "new_path": str(new_path.resolve())
        })

    def save_session(self) -> Optional[Path]:
        if not self.current_session_id or not self.current_session_files:
            return None

        log_file = self.log_dir / f"session_{self.current_session_id}.json"
        session_data = {
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "target_directory": self.target_directory,
            "total_files": len(self.current_session_files),
            "moved_files": self.current_session_files
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4, ensure_ascii=False)

        return log_file

    def get_latest_valid_session_log(self) -> Optional[Path]:
        """Retorna o caminho do log valido mais recente, ignorando arquivos vazios/corrompidos."""
        log_files = sorted(self.log_dir.glob("session_*.json"), reverse=True)
        for log_file in log_files:
            if log_file.stat().st_size > 0:
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        json.load(f)
                    return log_file
                except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError):
                    continue
        return None

    def undo_session(self, log_file_path: Optional[Path] = None, progress_callback=None) -> Dict[str, int]:
        if log_file_path is None:
            log_file_path = self.get_latest_valid_session_log()

        if not log_file_path or not log_file_path.exists():
            raise FileNotFoundError("Nenhum histórico válido de organização foi encontrado para desfazer.")

        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
        except Exception as e:
            raise ValueError(f"O arquivo de log está inacessível ou corrompido: {e}")

        moved_files = session_data.get("moved_files", [])
        total_files = len(moved_files)

        restored_count = 0
        error_count = 0

        for index, entry in enumerate(reversed(moved_files), start=1):
            curr_path = Path(entry["new_path"])
            orig_path = Path(entry["original_path"])

            try:
                if curr_path.exists():
                    orig_path.parent.mkdir(parents=True, exist_ok=True)
                    final_dest = self._get_safe_destination(orig_path)
                    shutil.move(str(curr_path), str(final_dest))
                    restored_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"Erro ao reverter '{curr_path.name}': {e}")
                error_count += 1

            if progress_callback:
                progress_callback(index, total_files)

        target_dir = session_data.get("target_directory")
        if target_dir:
            self._cleanup_empty_directories(Path(target_dir))

        log_file_path.unlink(missing_ok=True)
        return {"restored": restored_count, "errors": error_count}

    @staticmethod
    def _get_safe_destination(destination: Path) -> Path:
        if not destination.exists():
            return destination

        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        counter = 1

        while destination.exists():
            new_name = f"{stem}_restored_{counter}{suffix}"
            destination = parent / new_name
            counter += 1

        return destination

    @staticmethod
    def _cleanup_empty_directories(root_path: Path) -> None:
        if not root_path.exists() or not root_path.is_dir():
            return

        for path in sorted(root_path.rglob("*"), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass