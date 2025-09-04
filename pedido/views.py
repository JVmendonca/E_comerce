from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse 
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from produto.models import Variacao
from utils import utils
from . models import Pedido, ItemPedido


class DispatchLoginRequired(View):
     # para caso de alguem acessar a aba de pagar sem estar logado
     def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(*args, **kwargs)



class Pagar(DispatchLoginRequired, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'

    # para nao ter como acessar outro pedido de outra pessoa
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs


class SalvarPedido(View):
    template_name = 'pedido/pagar.html'

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.error(
                self.request,
                'Necessario criar um perfil para concluir a compra')
            return redirect('perfil:criar')
        
        if not request.session.get('carrinho'):
            messages.error(
                self.request,
                'carrinho vazio')
            return redirect('produto:lista')
        
        carrinho = self.request.session['carrinho']
        carrinho_variacao_ids = [v for v in carrinho]
        bd_variacoes = list(
            Variacao.objects.select_related('produto').filter(id__in=carrinho_variacao_ids)
            )
        
        for variacao in bd_variacoes:
            vid = str(variacao.id) # type: ignore

            estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']

            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque *preco_unt
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * preco_unt_promo


                error_msg_estoque = f'Estoque insuficiente para {variacao} no carrinho, ajustamos para {estoque} confira'
                

            if error_msg_estoque:
                messages.error(
                    self.request,
                    error_msg_estoque
                )

                self.request.session.save()
                return redirect('produto:carrinho')
            
        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_totals(carrinho)

        pedido = Pedido(
            usuario=self.request.user,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C'
        )

        pedido.save()
        
        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                ) for v in carrinho.values()
            ]
        )

        del self.request.session['carrinho']
        return redirect(
            reverse(
                'pedido:pagar',
            kwargs={'pk': pedido.pk}
            )
        )

class detalhe(View):
    pass

class Lista(View):
    pass
    