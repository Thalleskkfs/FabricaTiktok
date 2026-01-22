# RUN_WINDOWS

Guia rápido para executar o projeto no Windows.

## 1) Abrir o terminal no projeto

Abra o PowerShell e navegue até o projeto:

```powershell
cd D:\Dinheiros\tiktok-fabrica
```

## 2) Criar e ativar o virtualenv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, rode:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois, ative novamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3) Instalar dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Verificar o ambiente

```powershell
python -m src.env_check
```

Esse comando mostra o caminho do Python, o `sys.path` e o status dos imports essenciais.

## 5) Rodar o pipeline

```powershell
python -m src.pipeline_semana
```

## Observações (MoviePy, ffmpeg e fontes)

- **ffmpeg**: o MoviePy depende do ffmpeg para gerar vídeos.
  - Recomendado: instalar o ffmpeg e garantir que `ffmpeg.exe` esteja no PATH.
  - Exemplo de instalador: https://www.gyan.dev/ffmpeg/builds/

- **Fontes**: alguns recursos de texto do MoviePy dependem de fontes instaladas no sistema.
  - Se ocorrerem erros com `TextClip`, instale fontes adicionais ou ajuste as fontes no código.

- **Permissões**: se o MoviePy não encontrar o ffmpeg, verifique o PATH e reinicie o terminal.
