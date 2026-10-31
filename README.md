# 📁 Auto File Organizer



O **Auto File Organizer** é uma aplicação desktop para Windows desenvolvida em Python que organiza automaticamente ficheiros em pastas com base no seu tipo de extensão e organiza fotografias por **Ano/Mês** através da leitura de metadados EXIF.



---



## 🚀 Funcionalidades



- **Classificação por Categoria:** Mapeia e organiza ficheiros (Documentos, Vídeos, Áudios, Compactados, Instaladores, etc.) em subpastas dedicadas.

- **Organização Inteligente de Fotos:** Lê metadados EXIF de fotografias (`.jpg`, `.jpeg`, `.png`, etc.) e cria uma estrutura organizada por ano e mês (ex: `Imagens/2026/10-Outubro/`).

- **Tratamento de Duplicados:** Evita a sobrescrita acidental de ficheiros renomeando cópias existentes de forma automática (`ficheiro_1.pdf`).

- **Interface Visual Moderna:** Desenvolvida em CustomTkinter com suporte nativo ao tema escuro do Windows.

- **Executável Standalone:** Pode ser utilizado como um ficheiro `.exe` sem necessidade de instalar o Python.



---



## 🛠️ Tecnologias Utilizadas



- **Linguagem:** Python 3.12+

- **Interface Gráfica:** CustomTkinter

- **Processamento de Imagens:** Pillow (`PIL`)

- **Compilação:** PyInstaller

- **Estruturação de Projetos:** `pathlib` e `shutil`



---



## 💻 Como Executar o Código-Fonte



### Pré-requisitos

- Python instalado na máquina (versão 3.10 ou superior).



### Instalação



1. Clone o repositório:

   ```bash

   git clone https://github.com/Gabriel31Cezar/auto-file-organizer.git

   cd auto-file-organizer

   ```



2. Crie e ative um ambiente virtual (opcional, mas recomendado):

   ```bash

   python -m venv .venv

   .venv\Scripts\activate

   ```



3. Instale as dependências:

   ```bash

   pip install -r requirements.txt

   ```



4. Execute a aplicação:

   ```bash

   python main.py

   ```



---



## 📦 Como Compilar o Executável (`.exe`)



Para gerar o ficheiro executável autónomo dentro da pasta `dist/`, execute o script de compilação:



```bash

python build.py

```



---



## 👤 Autor



Desenvolvido por **Gabriel Cezar**.

# 📁 Auto File Organizer

[📥 **Baixar Executável (.exe) - Versão 2.0.0**](https://github.com/Gabriel31Cezar/auto-file-organizer/releases/latest)

---

## 🚀 Funcionalidades (v2.0.0)

- **Classificação por Categoria:** Mapeia e organiza ficheiros (Documentos, Vídeos, Áudios, Compactados, Instaladores, etc.) em subpastas dedicadas.
- **Varredura Recursiva Profunda:** Organiza ficheiros em pastas que possuem subpastas dentro de subpastas, consolidando a estrutura sem deixar ficheiros esquecidos.
- **Organização Temporal Universal:** Organiza **todos os tipos de ficheiros** por Ano e Mês (ex: `Documentos/2026/10-Outubro/`), utilizando EXIF para fotos e a data do SO para os demais ficheiros.
- **Alta Performance sem Travar:** Processamento em segundo plano (*Multithreading*) e Barra de Progresso em tempo real que suportam grandes volumes de dados mantendo a janela fluida.
- **Tratamento de Duplicados & Segurança:** Renomeação automática para evitar sobrescritas, trava antiloop e limpeza automática de pastas vazias remanescentes.
- **Interface Visual Moderna:** Desenvolvida em CustomTkinter com suporte nativo ao tema escuro do Windows.
- **Executável Standalone:** Pode ser utilizado como um ficheiro `.exe` sem necessidade de instalar o Python.

---

## 🆕 Novidades do Update 3.0.0 (Custom & Safe Control)

A versão **v3.0.0** traz um salto de performance, flexibilidade e segurança para a organização de arquivos:

- 🔍 **Análise Prévia & Seleção Interativa (Preview):** Escaneamento em segundo plano que lista todos os arquivos encontrados em subpastas em uma janela com *checkboxes*, permitindo selecionar exatamente o que mover ou filtrar por extensão (ex: `.pdf`).
- 🏷️ **Personalização dos Nomes das Pastas:** Liberdade para renomear os diretórios de destino da 1ª camada (ex: alterar `Documentos` para `01_Documentos_Trabalho`) antes de organizar.
- 🔄 **Sistema Transacional de Reversão (Undo):** Registro automático em log `.json` de cada movimentação para desfazer e restaurar 100% dos arquivos às suas localizações originais com auto-limpeza de pastas vazias.
- 🛡️ **Proteção Automática de Pastas de Projetos:** Reconhecimento de marcadores de desenvolvimento (`.git`, `package.json`, `requirements.txt`, etc.) para não desestruturar pastas organizadas manualmente pelo usuário.
- ⚡ **Alta Performance Multithread:** Escaneamento assíncrono e renderização em lote na interface gráfica, processando diretórios pesados (1.000+ arquivos) sem travar ou congelar a janela do Windows.

---