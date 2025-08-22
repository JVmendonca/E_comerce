def formata_preco(val):
    """Formata o preço para exibição com duas casas decimais."""
    return f"R$ {val:.2f}".replace('.', ',')