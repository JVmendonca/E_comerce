from django.shortcuts import render
from django.views.generic import ListView
from django.views import View


class ListaProdutos(ListView):
    pass

class DetalheProduto(View):
    pass

class AdicionarAoCarrinho(View):
    pass

class RemoverDoCarrinho(View):
    pass

class Carrinho(View):
    pass

class Finalizar(View):
    pass
