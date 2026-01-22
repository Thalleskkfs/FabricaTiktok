def main():
    config = carregar_config("config/config.yaml")

    # 1) Gerar roteiros
    scripts = m1_roteiros.gerar_roteiros(config)

    # 2) (opcional) Curadoria rápida humana
    scripts_aprovados = filtrar_scripts_manualmente(scripts)
    # Isso pode ser: abrir um .json, apagar os que você não gostou e salvar de novo

    # 3) Tradução / ajuste
    scripts_traduzidos = m2_traducao.processar(scripts_aprovados, config)

    # 4) Gerar vídeos com avatar
    m3_avatar_video.gerar_videos(scripts_traduzidos, config)

    # 5) Aplicar template / legendas
    m4_template_editor.processar_videos(config)

    # 6) Organizar tudo em lote
    m5_organizador.organizar_lote(config)

    print("✅ Lote gerado com sucesso!")

if __name__ == "__main__":
    main()
