from django.db import models
from PIL import Image
import os
from django.conf import settings
from django.utils.text import slugify
from utils import utils

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(upload_to='produtos_imagens/%y/%m/%d/'
                               , blank=True, null=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    preco_marketing = models.FloatField(verbose_name='preço')
    preco_marketing_promocional = models.FloatField(default=0, verbose_name='preço promo')
    tipo = models.CharField(default= 'v', max_length=1, choices=[
        ('V', 'Variável'),
        ('S', 'Simples'),
    ])

    def get_preco_formatado(self):
        return utils.formata_preco(self.preco_marketing)
    get_preco_formatado.short_description = 'Preço'
    
    def get_preco_formatado_promocional(self):
        return utils.formata_preco(self.preco_marketing_promocional)
    get_preco_formatado_promocional.short_description = 'Preço Promo'

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_height = img_pil.size

        if original_width <= new_width:
            img_pil.close()
            return
            
        
        new_height = round(new_width * original_width) / original_height

        new_img = img_pil.resize((new_width, int(new_height)), Image.Resampling.LANCZOS)
        new_img.save(img_full_path, optimize=True, quality=50)
        
        
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug


        super().save(*args, **kwargs)

        max_imagem_safe = 800

        if self.imagem:
            self.resize_image(self.imagem, max_imagem_safe)


    def __str__(self):
        return self.nome

class Variacao(models.Model):
    nome = models.CharField(max_length=50, blank=True, null=True )
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - {self.produto.nome}"

    class Meta:
        verbose_name = 'variacao'
        verbose_name_plural = 'variacoes'