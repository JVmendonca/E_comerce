from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from . import models
from django.db.models import Q
from perfil.models import Perfil
 
from produto import models
 
class ListaProdutos(ListView):
   model = models.Produto
   template_name = 'produto/lista.html'
   context_object_name = 'produtos'
   paginate_by = 3
#    ordering = ['-id'] caso queira ordenar para o ultimo produto add


class Busca(ListaProdutos):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo')
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs
        
        qs = qs.filter(
            Q(nome__icontains=termo) | 
            Q(descricao_curta__icontains=termo) |
            Q(descricao_longa__icontains=termo)
        )

        return qs
 
 
class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'
 
class Carrinho(View):
   def get(self, *args, **kwarg):
       contexto = {
           'carrinho': self.request.session.get('carrinho', {})
       }
       return render(self.request, 'produto/carrinho.html', contexto)
  

class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variacao_id = str(self.request.GET.get('vid'))

        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto

        produto_id = produto.id # type: ignore
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        if variacao.estoque < 1:
            messages.error(
                self.request,
                'Estoque insuficiente'
            )
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho}x no '
                    f'produto "{produto_nome}". Adicionamos {variacao_estoque}x '
                    f'no seu carrinho.'
                )
                quantidade_carrinho = variacao_estoque

            # Atualize todos os campos, não só quantidade!
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario * quantidade_carrinho,
                'preco_quantitativo_promocional': preco_unitario_promocional * quantidade_carrinho,
                'quantidade': quantidade_carrinho,
                'slug': slug,
                'imagem': imagem,
            }
        else:
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': 1,
                'slug': slug,
                'imagem': imagem,
            }

        print(carrinho)
        self.request.session.save()

        messages.success(
            self.request,
            f'Produto {produto_nome} {variacao_nome} adicionado ao seu '
            f'carrinho {carrinho[variacao_id]["quantidade"]}x.'
        )

        return redirect(http_referer)

 
class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        print('RemoverDoCarrinho foi chamada')
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variacao_id = str(self.request.GET.get('vid'))

        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        carrinho = self.request.session['carrinho']

        if variacao_id not in carrinho:
            return redirect(http_referer)

        # Pegue o item antes de remover
        item = carrinho[variacao_id]

        messages.success(
            self.request,
            f'Produto {item["produto_nome"]} {item["variacao_nome"]} removido do seu carrinho.'
        )

        del carrinho[variacao_id]
        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        return redirect(http_referer or reverse('produto:carrinho'))
 
 
class ResumoDaCompra(View):
   def get(self, *args, **kwarg):
      if not self.request.user.is_authenticated:
          return redirect('perfil:criar')
      
      perfil = Perfil.objects.filter(usuario=self.request.user).exists()
      
      if not perfil:
          messages.error(
              self.request,
              'Necessario criar um perfil para concluir a compra'
          )
          return redirect('perfil:criar')
      
      if not self.request.session.get('carrinho'):
          messages.error(
              self.request,
              'Nenhum produto no carrinho'
          )
          return redirect('produto:lista')
          
         
      contexto = {
          'usuario': self.request.user,
          'carrinho': self.request.session.get('carrinho', {})
      }
      return render(self.request, 'produto/resumodacompra.html', contexto) 
   
