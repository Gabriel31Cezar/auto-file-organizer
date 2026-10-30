from datetime import datetime
from pathlib import Path
from PIL import Image, ExifTags


def get_file_date(file_path: Path) -> tuple[str, str]:
    """Extrai a data de qualquer ficheiro.

    Se for uma imagem com EXIF, lê a data da tiragem. Caso contrário (ou para
    outros tipos de ficheiros), utiliza a data de modificação/criação do
    sistema.

    Retorna uma tupla: (Ano, Mês-Nome), ex: ('2026', '10-Outubro')
    """
    date_found = None

    # Extensões de imagem elegíveis para leitura EXIF
    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".webp",
        ".heic",
    }

    # 1. Tenta ler EXIF se for uma imagem
    if file_path.suffix.lower() in image_extensions:
        try:
            with Image.open(file_path) as img:
                exif = img.getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag_name in ["DateTimeOriginal", "DateTime"]:
                            date_found = datetime.strptime(
                                str(value), "%Y:%m:%d %H:%M:%S"
                            )
                            break
        except (AttributeError, KeyError, IndexError, ValueError, OSError):
            pass

    # 2. Fallback Universal: Lê a data de modificação do ficheiro no SO
    if not date_found:
        try:
            timestamp = file_path.stat().st_mtime
            date_found = datetime.fromtimestamp(timestamp)
        except (OSError, AttributeError, ValueError):
            date_found = datetime.now()

    # Formatação padronizada de Ano e Mês
    year = str(date_found.year)

    months = {
        1: "01-Janeiro",
        2: "02-Fevereiro",
        3: "03-Março",
        4: "04-Abril",
        5: "05-Maio",
        6: "06-Junho",
        7: "07-Julho",
        8: "08-Agosto",
        9: "09-Setembro",
        10: "10-Outubro",
        11: "11-Novembro",
        12: "12-Dezembro",
    }

    month_folder = months.get(date_found.month, "00-Outros")

    return year, month_folder