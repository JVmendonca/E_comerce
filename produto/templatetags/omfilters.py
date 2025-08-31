from django.template import Library
from utils import utils

register = Library()


@register.filter
def formata_preco(val):
    """Formata o preço para exibição com duas casas decimais."""
    return utils.formata_preco(val)

@register.filter
def cart_total_qtd(carrinho):
    """Calcula o total do carrinho."""
    return utils.cart_total_qtd(carrinho)