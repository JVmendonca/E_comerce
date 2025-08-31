def formata_preco(val):
    """Formata o preço para exibição com duas casas decimais."""
    return f"R$ {val:.2f}".replace('.', ',')

def cart_total_qtd(carrinho):
    """Calcula o total do carrinho."""
    return sum([item['quantidade'] for item in carrinho.values()])
    


def cart_totals(carrinho):
    return sum(
        [
            item.get('preco_quantitativo_promocional')
            if item.get('preco_quantitativo_promocional')
            else item.get('preco_quantitativo')
            for item 
            in carrinho.values()
        ]
    )