from pathlib import Path
from app.core.organizer import organize_directory

# 1. Cria uma pasta temporária de teste dentro do projeto
test_folder = Path("pasta_teste")
test_folder.mkdir(exist_ok=True)

# 2. Cria alguns ficheiros fictícios de teste
(test_folder / "documento.pdf").touch()
(test_folder / "foto.png").touch()
(test_folder / "musica.mp3").touch()
(test_folder / "programa.exe").touch()

print("Ficheiros de teste criados com sucesso na 'pasta_teste'!")

# 3. Executa a nossa lógica de organização
resultado = organize_directory(str(test_folder))

# 4. Exibe o resumo do que foi movido
print("\nResumo da organização:")
for categoria, quantidade in resultado.items():
    if quantidade > 0:
        print(f" - {categoria}: {quantidade} ficheiro(s)")