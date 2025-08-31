def formata_preco(val):
    """Formata o preço para exibição com duas casas decimais."""
    return f"R$ {val:.2f}".replace('.', ',')

def cart_total_qtd(carrinho):
    """Calcula o total do carrinho."""
    total = sum([item['quantidade'] for item in carrinho.values()])
    return total