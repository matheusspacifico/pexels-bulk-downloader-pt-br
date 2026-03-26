# 📸 Pexels Bulk Downloader

CLI interativo para baixar fotos da [Pexels](https://www.pexels.com) em massa. Perfeito pra quem produz conteúdo e precisa de várias imagens de uma vez sem ficar pesquisando uma por uma.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/Licença-MIT-green)

---

## Features

- CLI bonito e colorido com menus interativos
- Salva sua API key localmente (configura uma vez só)
- Filtro por orientação: vertical (TikTok/Reels), horizontal ou quadrado
- Escolha o tamanho: original, large2x, large, medium, small
- Organiza as fotos em subpastas por termo de busca
- Pula fotos que já foram baixadas (cache)
- Relatório completo no final com status de cada busca
- Funciona tanto no modo interativo quanto com flags no terminal

---

## Pré-requisitos

- **Python 3.10+** instalado
- Uma **API key da Pexels** (grátis) → [https://www.pexels.com/api/](https://www.pexels.com/api/)

---

## Instalação

### Linux / macOS

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/pexels-bulk-downloader.git
cd pexels-bulk-downloader

# Crie e ative uma virtual environment
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install requests rich
```

### Windows (CMD)

```cmd
:: Clone o repositório
git clone https://github.com/seu-usuario/pexels-bulk-downloader.git
cd pexels-bulk-downloader

:: Crie e ative uma virtual environment
python -m venv venv
venv\Scripts\activate

:: Instale as dependências
pip install requests rich
```

### Windows (PowerShell)

```powershell
# Clone o repositório
git clone https://github.com/seu-usuario/pexels-bulk-downloader.git
cd pexels-bulk-downloader

# Crie e ative uma virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# Instale as dependências
pip install requests rich
```

> **Nota PowerShell:** se der erro de permissão ao ativar a venv, rode antes:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## Configuração da API Key

Antes de baixar qualquer foto, você precisa configurar sua API key:

```bash
python pexels_cli.py config
```

O CLI vai pedir sua key, validar contra a API da Pexels, e salvar num arquivo `.pexels_config.json` no mesmo diretório. Você só precisa fazer isso uma vez.

> **Como pegar a key:** acesse [pexels.com/api](https://www.pexels.com/api/), crie uma conta (é grátis e instantâneo), e copie a key que aparece no dashboard.

---

## Como usar

### Modo interativo (mais fácil)

Só rode sem argumentos e o CLI vai te guiando:

```bash
python pexels_cli.py
```

### Download rápido com argumentos

```bash
python pexels_cli.py download -q "dog on beach, sunset ocean, tropical island" -n 5 --portrait
```

### Todos os argumentos disponíveis

| Flag | Descrição | Padrão |
|---|---|---|
| `-q`, `--queries` | Termos de busca separados por vírgula | *(pergunta interativamente)* |
| `-n`, `--num` | Quantidade de fotos por termo | `3` |
| `-o`, `--output` | Pasta de saída | `pexels_photos` |
| `-s`, `--size` | Tamanho: `original`, `large2x`, `large`, `medium`, `small` | `large` |
| `--portrait` | Orientação vertical (ideal pra TikTok/Reels) | padrão |
| `--landscape` | Orientação horizontal | |
| `--square` | Orientação quadrada | |

---

## Exemplos práticos

**Baixar fotos pra um vídeo sobre IA (vertical, estilo TikTok):**

```bash
python pexels_cli.py download --portrait -q "person scrolling phone, confused person thinking, robot and human, digital brain, face recognition technology, neural network, smart home device"
```

**Baixar 10 fotos de paisagem em alta resolução:**

```bash
python pexels_cli.py download -q "mountain landscape, ocean sunset" -n 10 -s original --landscape
```

**Baixar pra uma pasta específica:**

```bash
python pexels_cli.py download -q "coffee shop, workspace minimal" -o fotos_projeto -n 5
```

---

## Estrutura de saída

O script cria uma pasta organizada assim:

```
pexels_photos/
├── person_scrolling_phone/
│   ├── person_scrolling_phone_1_john_doe.jpg
│   ├── person_scrolling_phone_2_jane_smith.jpg
│   └── person_scrolling_phone_3_alex_wong.jpg
├── confused_person_thinking/
│   ├── confused_person_thinking_1_maria_silva.jpg
│   └── ...
├── robot_and_human/
│   └── ...
└── ...
```

Cada subpasta corresponde a um termo de busca, e cada foto inclui o nome do fotógrafo no arquivo.

---

## Uso no dia a dia

Sempre que abrir um terminal novo, lembre de ativar a venv antes de rodar o script:

```bash
# Linux / macOS
source venv/bin/activate

# Windows CMD
venv\Scripts\activate

# Windows PowerShell
venv\Scripts\Activate.ps1
```

Pra desativar a venv quando terminar:

```bash
deactivate
```

---

## Licença

MIT — use como quiser.

---

## Créditos

Fotos fornecidas pela [Pexels](https://www.pexels.com). Todas as fotos baixadas são livres para uso pessoal e comercial conforme os [termos da Pexels](https://www.pexels.com/license/).
