import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.core.organizer import organize_directory, CATEGORY_MAP

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela Principal
        self.title("Auto File Organizer v2.0.0")
        self.geometry("580x420")
        self.resizable(False, False)

        # Ícone da Janela
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        # --- TÍTULO DA APLICAÇÃO ---
        self.title_label = ctk.CTkLabel(
            self,
            text="Organizador Automático de Ficheiros",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(padx=20, pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Selecione uma pasta para organizar todos os ficheiros por categoria e data.",
            font=ctk.CTkFont(size=12)
        )
        self.subtitle_label.pack(padx=20, pady=(0, 15))

        # --- ÁREA DE SELEÇÃO DE PASTA ---
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(padx=20, pady=10, fill="x")

        self.path_entry = ctk.CTkEntry(
            self.path_frame,
            placeholder_text="Nenhuma pasta selecionada...",
            width=390
        )
        self.path_entry.pack(side="left", padx=(10, 5), pady=10)

        self.browse_button = ctk.CTkButton(
            self.path_frame,
            text="Procurar...",
            width=100,
            command=self.select_folder
        )
        self.browse_button.pack(side="right", padx=(5, 10), pady=10)

        # --- BOTÃO DE AÇÃO ---
        self.organize_button = ctk.CTkButton(
            self,
            text="Organizar Pasta",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.start_organization_thread
        )
        self.organize_button.pack(padx=20, pady=(15, 10), fill="x")

        # --- BARRA DE PROGRESSO VISUAL ---
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.pack(padx=20, pady=(10, 5), fill="x")
        self.progress_bar.set(0)  # Inicia zerada

        # --- ETIQUETA DE STATUS E RECTO ---
        self.status_label = ctk.CTkLabel(
            self,
            text="Aguardando seleção de pasta.",
            text_color="gray"
        )
        self.status_label.pack(padx=20, pady=5)

    def select_folder(self):
        """Abre a janela de diálogo do SO para escolher uma pasta."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_selected)
            self.status_label.configure(text="Pasta pronta para ser organizada.", text_color="green")
            self.progress_bar.set(0)

    def start_organization_thread(self):
        """Inicia o processo de organização numa thread separada para não travar a GUI."""
        target_path = self.path_entry.get().strip()

        if not target_path:
            messagebox.showwarning("Aviso", "Por favor, selecione uma pasta primeiro.")
            return

        path_obj = Path(target_path)
        if not path_obj.exists() or not path_obj.is_dir():
            messagebox.showerror("Erro", "A pasta selecionada não é válida.")
            return

        # Desativa controles para evitar cliques duplicados
        self.organize_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.status_label.configure(text="A analisar ficheiros e estrutura...", text_color="orange")
        self.progress_bar.set(0)

        # Executa em segundo plano via Threading
        threading.Thread(target=self._run_organization_worker, args=(target_path,), daemon=True).start()

    def _run_organization_worker(self, target_path: str):
        """Worker que roda em segundo plano e atualiza o progresso visual."""
        try:
            root_folder = Path(target_path).resolve()
            reserved_categories = set(CATEGORY_MAP.keys()) | {"Outros"}

            # Mapeia ficheiros válidos para calcular o total
            all_files = [
                p for p in root_folder.rglob("*")
                if p.is_file()
                and p.relative_to(root_folder).parts[0] not in reserved_categories
                and not p.name.startswith(".")
                and p.suffix.lower() not in [".tmp", ".crdownload", ".part"]
            ]

            total_files = len(all_files)

            if total_files == 0:
                self._update_ui_finished(0, "Nenhum ficheiro novo para organizar.")
                return

            # Callback para atualizar a barra de progresso em tempo real
            def progress_callback(current, total):
                progress = current / total
                self.progress_bar.set(progress)
                self.status_label.configure(
                    text=f"A organizar ficheiros... ({current}/{total})",
                    text_color="orange"
                )

            # Executa a lógica do backend
            summary = organize_directory(target_path, progress_callback=progress_callback)
            total_moved = sum(summary.values())

            self._update_ui_finished(total_moved, f"Concluído! {total_moved} ficheiro(s) organizado(s).")

        except Exception as e:
            self._update_ui_error(str(e))

    def _update_ui_finished(self, total_moved: int, message: str):
        """Restaura a interface após o término do processo."""
        self.progress_bar.set(1.0 if total_moved > 0 else 0)
        self.status_label.configure(text=message, text_color="green")
        self.organize_button.configure(state="normal")
        self.browse_button.configure(state="normal")
        messagebox.showinfo("Sucesso", f"Organização concluída com sucesso!\nTotal de ficheiros movidos: {total_moved}")

    def _update_ui_error(self, error_msg: str):
        """Restaura a interface em caso de erro."""
        self.progress_bar.set(0)
        self.status_label.configure(text="Erro ao organizar.", text_color="red")
        self.organize_button.configure(state="normal")
        self.browse_button.configure(state="normal")
        messagebox.showerror("Erro de Execução", f"Ocorreu um erro: {error_msg}")