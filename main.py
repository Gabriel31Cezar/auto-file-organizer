from pathlib import Path
from PIL import Image
from app.core.organizer import organize_directory

# 1. Cria uma pasta temporária para o teste
test_folder = Path("pasta_teste_exif")
test_folder.mkdir(exist_ok=True)

# 2. Cria uma imagem real fictícia usando o Pillow (para testar a leitura de data)
img = Image.new("RGB", (100, 100), color="blue")
img.save(test_folder / "minha_foto.jpg")

# 3. Cria um documento comum
(test_folder / "relatorio.pdf").touch()

print("Ficheiros de teste criados na 'pasta_teste_exif'!")

# 4. Executa a organização com o novo motor integrado
resultado = organize_directory(str(test_folder))

print("\nResumo da organização:")
for categoria, quantidade in resultado.items():
    if quantidade > 0:
        print(f" - {categoria}: {quantidade} ficheiro(s)")

print("\nVerificando a estrutura de pastas criada para a imagem:")
for path in test_folder.rglob("*"):
    if path.is_file():
        print(f" 📂 Ficheiro movido para: {path}")