import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

# Importamos a função de organização que criámos no core
from app.core.organizer import organize_directory

# Configuração global de aparência do CustomTkinter
ctk.set_appearance_mode("System")  # Segue o tema do sistema (Escuro ou Claro)
ctk.set_default_color_theme("blue")  # Tema de cor dos botões


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela Principal
        self.title("Auto File Organizer")
        self.geometry("550 x 350")
        self.resizable(False, False)

        # --- TÍTULO DA APLICAÇÃO ---
        self.title_label = ctk.CTkLabel(
            self,
            text="Organizador Automático de Ficheiros",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(padx=20, pady=(20, 10))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Selecione uma pasta para organizar os seus ficheiros por categoria e data.",
            font=ctk.CTkFont(size=12)
        )
        self.subtitle_label.pack(padx=20, pady=(0, 20))

        # --- ÁREA DE SELEÇÃO DE PASTA ---
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(padx=20, pady=10, fill="x")

        self.path_entry = ctk.CTkEntry(
            self.path_frame,
            placeholder_text="Nenhuma pasta selecionada...",
            width=360
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
            command=self.run_organization
        )
        self.organize_button.pack(padx=20, pady=(20, 10), fill="x")

        # --- ETIQUETA DE STATUS ---
        self.status_label = ctk.CTkLabel(
            self,
            text="Aguardando seleção de pasta.",
            text_color="gray"
        )
        self.status_label.pack(padx=20, pady=10)

    def select_folder(self):
        """Abre a janela de diálogo do sistema operacional para escolher uma pasta."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_selected)
            self.status_label.configure(text="Pasta pronta para ser organizada.", text_color="green")

    def run_organization(self):
        """Chama a lógica de organização e exibe o resultado."""
        target_path = self.path_entry.get().strip()

        if not target_path:
            messagebox.showwarning("Aviso", "Por favor, selecione uma pasta primeiro.")
            return

        path_obj = Path(target_path)
        if not path_obj.exists() or not path_obj.is_dir():
            messagebox.showerror("Erro", "A pasta selecionada não é válida.")
            return

        try:
            self.status_label.configure(text="A organizar ficheiros...", text_color="orange")
            self.update_idletasks()

            # Executa a nossa lógica do backend
            summary = organize_directory(target_path)

            total_moved = sum(summary.values())

            self.status_label.configure(
                text=f"Concluído! {total_moved} ficheiro(s) organizado(s).",
                text_color="green"
            )
            messagebox.showinfo("Sucesso",
                                f"Organização concluída com sucesso!\nTotal de ficheiros movidos: {total_moved}")

        except Exception as e:
            self.status_label.configure(text="Erro ao organizar.", text_color="red")
            messagebox.showerror("Erro de Execução", f"Ocorreu um erro: {str(e)}")