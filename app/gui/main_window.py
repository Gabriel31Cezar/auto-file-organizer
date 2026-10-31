import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import List, Dict, Any

from app.core.analyzer import DirectoryAnalyzer
from app.core.organizer import organize_selected_files
from app.core.history_logger import HistoryLogger
from app.core.config_manager import ConfigManager
from app.gui.selection_dialog import SelectionDialog

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto File Organizer v3.0.0")
        self.geometry("620x520")
        self.resizable(False, False)

        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        self.title_label = ctk.CTkLabel(
            self,
            text="Organizador Automático de Ficheiros",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(padx=20, pady=(15, 2))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Selecione uma pasta para analisar, escolher ficheiros ou desfazer alterações.",
            font=ctk.CTkFont(size=12)
        )
        self.subtitle_label.pack(padx=20, pady=(0, 10))

        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(padx=20, pady=5, fill="x")

        self.path_entry = ctk.CTkEntry(
            self.path_frame,
            placeholder_text="Nenhuma pasta selecionada...",
            width=430
        )
        self.path_entry.pack(side="left", padx=(10, 5), pady=10)

        self.browse_button = ctk.CTkButton(
            self.path_frame,
            text="Procurar...",
            width=100,
            command=self.select_folder
        )
        self.browse_button.pack(side="right", padx=(5, 10), pady=10)

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(padx=20, pady=5, fill="x")

        self.config_manager = ConfigManager()
        self.protect_projects_switch = ctk.CTkSwitch(
            self.options_frame,
            text="Proteger pastas de projetos (.git, package.json, etc.)",
            command=self.toggle_project_protection
        )
        self.protect_projects_switch.pack(padx=15, pady=10, side="left")

        if self.config_manager.config_data.get("protect_project_folders", True):
            self.protect_projects_switch.select()
        else:
            self.protect_projects_switch.deselect()

        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(padx=20, pady=10, fill="x")

        self.organize_button = ctk.CTkButton(
            self.actions_frame,
            text="Analisar e Selecionar Ficheiros",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            command=self.start_analysis_thread
        )
        self.organize_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.undo_button = ctk.CTkButton(
            self.actions_frame,
            text="Desfazer (Undo)",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            fg_color="#A83232",
            hover_color="#7A2424",
            command=self.start_undo_thread
        )
        self.undo_button.pack(side="right", expand=True, fill="x", padx=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.pack(padx=20, pady=(10, 5), fill="x")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="Aguardando seleção de pasta.",
            text_color="gray"
        )
        self.status_label.pack(padx=20, pady=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_selected)
            self.status_label.configure(
                text="Pasta pronta para análise.",
                text_color="green"
            )
            self.progress_bar.set(0)

    def toggle_project_protection(self):
        is_active = bool(self.protect_projects_switch.get())
        self.config_manager.config_data["protect_project_folders"] = is_active
        self.config_manager.save_config()

    def start_analysis_thread(self):
        target_path = self.path_entry.get().strip()
        if not target_path or not Path(target_path).exists():
            messagebox.showwarning("Aviso", "Por favor, selecione uma pasta válida primeiro.")
            return

        self._set_ui_state("disabled")
        self.status_label.configure(text="A analisar ficheiros (aguarde)...", text_color="orange")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        threading.Thread(
            target=self._run_analysis_worker,
            args=(target_path,),
            daemon=True
        ).start()

    def _run_analysis_worker(self, target_path: str):
        try:
            analyzer = DirectoryAnalyzer(self.config_manager)
            analysis_data = analyzer.analyze_directory(target_path)
            self.after(0, self._on_analysis_complete, analysis_data)
        except Exception as e:
            self.after(0, self._on_operation_error, f"Falha ao analisar: {str(e)}")

    def _on_analysis_complete(self, analysis_data: Dict[str, Any]):
        self._stop_progress_bar()
        self._set_ui_state("normal")

        if not analysis_data["files"]:
            self.status_label.configure(text="Nenhum ficheiro elegível encontrado.", text_color="gray")
            messagebox.showinfo("Informação", "Nenhum ficheiro elegível foi encontrado para organizar.")
            return

        self.status_label.configure(text="Análise concluída. Selecione os ficheiros.", text_color="green")
        SelectionDialog(
            parent=self,
            analysis_data=analysis_data,
            on_confirm_callback=self.start_organization_thread
        )

    def start_organization_thread(self, selected_files: List[Dict[str, Any]], custom_folder_names: Dict[str, str]):
        target_path = self.path_entry.get().strip()

        self._set_ui_state("disabled")
        self.status_label.configure(text="A mover ficheiros selecionados...", text_color="orange")
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

        threading.Thread(
            target=self._run_organization_worker,
            args=(target_path, selected_files, custom_folder_names),
            daemon=True
        ).start()

    def _run_organization_worker(self, target_path: str, selected_files: List[Dict[str, Any]], custom_folder_names: Dict[str, str]):
        try:
            summary = organize_selected_files(
                target_path=target_path,
                selected_files=selected_files,
                custom_folder_names=custom_folder_names,
                progress_callback=self._update_progress
            )
            total_moved = sum(summary.values())
            self.after(0, self._on_organization_complete, total_moved)
        except Exception as e:
            self.after(0, self._on_operation_error, str(e))

    def start_undo_thread(self):
        self._set_ui_state("disabled")
        self.status_label.configure(text="A reverter última organização...", text_color="orange")
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

        threading.Thread(
            target=self._run_undo_worker,
            daemon=True
        ).start()

    def _run_undo_worker(self):
        try:
            logger = HistoryLogger()
            result = logger.undo_session(progress_callback=self._update_progress)
            self.after(0, self._on_undo_complete, result["restored"])
        except Exception as e:
            self.after(0, self._on_operation_error, str(e))

    def _update_progress(self, current: int, total: int):
        progress = current / total if total > 0 else 1.0
        self.after(0, lambda: self.progress_bar.set(progress))

    def _stop_progress_bar(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

    def _on_organization_complete(self, total_moved: int):
        self._set_ui_state("normal")
        self.status_label.configure(
            text=f"Concluído! {total_moved} ficheiro(s) organizado(s).",
            text_color="green"
        )
        messagebox.showinfo("Sucesso", f"Organização concluída!\nTotal de ficheiros movidos: {total_moved}")

    def _on_undo_complete(self, restored_count: int):
        self._set_ui_state("normal")
        self.status_label.configure(
            text=f"Reversão concluída! {restored_count} ficheiro(s) restaurado(s).",
            text_color="green"
        )
        messagebox.showinfo("Reversão Concluída", f"Operação desfeita com sucesso!\nFicheiros restaurados: {restored_count}")

    def _on_operation_error(self, error_msg: str):
        self._stop_progress_bar()
        self._set_ui_state("normal")
        self.status_label.configure(text="Erro na operação.", text_color="red")
        messagebox.showerror("Erro", f"Ocorreu uma falha: {error_msg}")

    def _set_ui_state(self, state: str):
        self.organize_button.configure(state=state)
        self.undo_button.configure(state=state)
        self.browse_button.configure(state=state)