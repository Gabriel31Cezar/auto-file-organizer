from datetime import datetime
from pathlib import Path
from PIL import Image, ExifTags


def get_photo_date(image_path: Path) -> tuple[str, str]:
    """Lê a data de uma foto através dos metadados EXIF.

    Se não encontrar metadados EXIF, utiliza a data de modificação do ficheiro.

    Retorna uma tupla contendo (Ano, Mês-Nome), por exemplo: ('2026',
    '10-Outubro')
    """
    date_taken = None

    # Tenta extrair a data original dos metadados EXIF da imagem
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            if exif:
                # Procura o código numérico correspondente à tag 'DateTimeOriginal' ou 'DateTime'
                for tag_id, value in exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag_name in ["DateTimeOriginal", "DateTime"]:
                        date_taken = datetime.strptime(
                            str(value), "%Y:%m:%d %H:%M:%S"
                        )
                        break
    except (AttributeError, KeyError, IndexError, ValueError, OSError):
        # Se ocorrer algum erro ao ler o EXIF ou ficheiro inválido, ignora a leitura
        pass

    # Caso a foto não tenha metadados EXIF, usa a data do ficheiro no sistema operacional
    if not date_taken:
        timestamp = image_path.stat().st_mtime
        date_taken = datetime.fromtimestamp(timestamp)

    # Formata a data em Ano e Mês
    year = str(date_taken.year)

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

    month_folder = months.get(date_taken.month, "00-Outros")

    return year, month_folder