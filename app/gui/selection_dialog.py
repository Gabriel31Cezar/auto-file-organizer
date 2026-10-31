import customtkinter as ctk
from tkinter import messagebox
from typing import List, Dict, Any


class SelectionDialog(ctk.CTkToplevel):
    """Janela de alta performance para seleção individual e customização dos nomes das pastas."""

    def __init__(self, parent, analysis_data: Dict[str, Any], on_confirm_callback):
        super().__init__(parent)

        self.title("Seleção de Ficheiros e Personalização de Pastas")
        self.geometry("780x640")
        self.resizable(True, True)

        self.analysis_data = analysis_data
        self.on_confirm_callback = on_confirm_callback
        self.file_checkboxes: List[Dict[str, Any]] = []

        self.grab_set()

        self.header_label = ctk.CTkLabel(
            self,
            text=f"Ficheiros Encontrados: {len(analysis_data['files'])} (Selecione abaixo)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.header_label.pack(padx=20, pady=(12, 5))

        self.folders_frame = ctk.CTkFrame(self)
        self.folders_frame.pack(padx=20, pady=5, fill="x")

        self.folders_title = ctk.CTkLabel(
            self.folders_frame,
            text="Personalizar nomes das pastas de destino (1ª Camada):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.folders_title.pack(padx=10, pady=(5, 5), anchor="w")

        self.category_entries: Dict[str, ctk.CTkEntry] = {}
        entries_inner_frame = ctk.CTkFrame(self.folders_frame, fg_color="transparent")
        entries_inner_frame.pack(padx=10, pady=5, fill="x")

        default_categories = ["Imagens", "Documentos", "Videos", "Audios", "Compactados", "Instaladores", "Outros"]
        for idx, cat in enumerate(default_categories):
            col = idx % 4
            row = idx // 4

            lbl = ctk.CTkLabel(entries_inner_frame, text=f"{cat}:", font=ctk.CTkFont(size=11))
            lbl.grid(row=row * 2, column=col, padx=5, pady=(2, 0), sticky="w")

            entry = ctk.CTkEntry(entries_inner_frame, width=160, placeholder_text=cat)
            entry.insert(0, cat)
            entry.grid(row=row * 2 + 1, column=col, padx=5, pady=(0, 5), sticky="w")
            self.category_entries[cat] = entry

        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(padx=20, pady=5, fill="x")

        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filtros Rápidos:", font=ctk.CTkFont(weight="bold"))
        self.filter_label.pack(side="left", padx=10, pady=5)

        self.btn_select_all = ctk.CTkButton(self.filter_frame, text="Marcar Todos", width=100, command=self.select_all)
        self.btn_select_all.pack(side="left", padx=5, pady=5)

        self.btn_deselect_all = ctk.CTkButton(self.filter_frame, text="Desmarcar Todos", width=110, command=self.deselect_all)
        self.btn_deselect_all.pack(side="left", padx=5, pady=5)

        self.btn_only_pdf = ctk.CTkButton(self.filter_frame, text="Apenas .PDF", width=90, command=lambda: self.select_by_ext(".pdf"))
        self.btn_only_pdf.pack(side="left", padx=5, pady=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Lista de Ficheiros Elegíveis")
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.populate_file_list()

        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(padx=20, pady=(5, 15), fill="x")

        self.confirm_button = ctk.CTkButton(
            self.footer_frame,
            text="Confirmar e Organizar Selecionados",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.confirm_selection
        )
        self.confirm_button.pack(fill="x")

    def populate_file_list(self):
        # Renderização em lote otimizada para evitar travamento da GUI
        files = self.analysis_data["files"]
        for idx, file_info in enumerate(files):
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(
                self.scroll_frame,
                text=f"{file_info['name']}  ({file_info['relative_path']}) -> [{file_info['suggested_category']}]",
                variable=var,
                font=ctk.CTkFont(size=11)
            )
            chk.pack(anchor="w", padx=10, pady=2)
            self.file_checkboxes.append({
                "info": file_info,
                "variable": var
            })

            # Atualiza o frame a cada 150 itens para não congelar pastas gigantes
            if idx % 150 == 0:
                self.update_idletasks()

    def select_all(self):
        for item in self.file_checkboxes:
            item["variable"].set(True)

    def deselect_all(self):
        for item in self.file_checkboxes:
            item["variable"].set(False)

    def select_by_ext(self, target_ext: str):
        for item in self.file_checkboxes:
            if item["info"]["extension"].lower() == target_ext.lower():
                item["variable"].set(True)
            else:
                item["variable"].set(False)

    def confirm_selection(self):
        selected_files = [item["info"] for item in self.file_checkboxes if item["variable"].get()]

        if not selected_files:
            messagebox.showwarning("Aviso", "Nenhum ficheiro foi selecionado para organizar.")
            return

        custom_folder_names = {
            cat: entry.get().strip() if entry.get().strip() else cat
            for cat, entry in self.category_entries.items()
        }

        self.destroy()
        self.on_confirm_callback(selected_files, custom_folder_names)