import os
import customtkinter
import PyInstaller.__main__

# Obtém o caminho do pacote CustomTkinter de forma segura para o analisador de tipos
ctk_file = customtkinter.__file__ or ""
ctk_path = os.path.dirname(ctk_file)

# Define os argumentos de compilação do PyInstaller
args = [
    "main.py",  # Ficheiro principal de entrada
    "--name=AutoFileOrganizer",  # Nome do executável final
    "--onefile",  # Empacota tudo num único ficheiro .exe
    "--noconsole",  # Esconde a janela preta do terminal ao abrir a aplicação
    f"--add-data={ctk_path};customtkinter/",  # Inclui os temas visuais do CustomTkinter
    "--clean",  # Limpa o cache de compilações anteriores
]

print("A iniciar o processo de compilação do executável .exe...")
PyInstaller.__main__.run(args)
print("\nCompilação concluída com sucesso! Verifique a pasta 'dist/'.")