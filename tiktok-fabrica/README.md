# FabricaTikTok

Pipeline automatizado para criar roteiros, traduzir, gerar vídeos base, aplicar template e organizar lotes prontos para postar no TikTok/Shorts.

## Componentes principais

- `src/pipeline_semana.py`: orquestra o fluxo semanal (M1 → M5).
- `src/m1_roteiros.py` … `src/m5_organizador.py`: módulos de roteiro, tradução, vídeo base, template e organização.
- `config/config.yaml`: configuração do lote (idiomas, nicho, quantidade, dry_run).
- `run_batch.py`: entrada principal com overrides via CLI.

## Instalação rápida

```bash
pip install -r requirements.txt
```

Para detalhes completos em Windows, veja `RUN_WINDOWS.md`.

## Verificação de ambiente

```bash
python -m src.env_check
```

## Executar o pipeline

```bash
python run_batch.py
```

### Overrides de CLI

```bash
python run_batch.py --niche psicologia_dark --videos 10 --dry-run
```

Parâmetros disponíveis:

- `--config PATH` (padrão: `config/config.yaml`)
- `--niche N`
- `--videos N`
- `--dry-run`
