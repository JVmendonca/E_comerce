from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
import re
from utils.validacpf import valida_cpf

class Perfil(models.Model):
    usuario = models.OneToOneField(User,
     on_delete=models.CASCADE,verbose_name='Usuário'
     )
    idade = models.PositiveIntegerField()
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11, unique=True)
    endereco = models.CharField(max_length=50, verbose_name='Endereço')
    numero = models.CharField(max_length=5)
    complemento = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=8)
    cidade = models.CharField(max_length=30)
    estado = models.CharField(
        max_length=2,
        default='SP',
        choices=[
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins')
        ]
    )
    def __str__(self):
        return f'{self.usuario}'
    
    def clean(self):
       mensagem_erro = {}

       if not valida_cpf(self.cpf):
           mensagem_erro['cpf'] = 'CPF inválido'
       
       if not re.search(r'[^0-9]', self.cep) or len(self.cep) != 8:
           mensagem_erro['cep'] = 'CEP inválido, digite 8 digitos do cep'
       if mensagem_erro:
           raise ValidationError(mensagem_erro)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['usuario__first_name', 'usuario__last_name']