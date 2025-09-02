from django import forms
from django.contrib.auth.models import User
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)


class UserForm(forms.ModelForm):
    password = forms.CharField(
         required=False,
         widget=forms.PasswordInput(),
         label='Senha'
         )
    password2 = forms.CharField(
         required=False,
         widget=forms.PasswordInput(),
         label='Confirmaçao Senha'
         )

    def __init__(self, usuario = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'password2','email')

    def clean(self, *args, **kwargs):
            data = self.data
            cleaned = self.cleaned_data

            validation_error_msg = {}

            usuario_data = cleaned.get('username')
            email_data = cleaned.get('email')
            password_data = cleaned.get('password')
            password2_data = cleaned.get('password2')

            usuario_db = User.objects.filter(username=data).first()
            email_db = User.objects.filter(email=data).first()

            #variaços para erros
            error_msg_user_exist = 'Username ja cadastrado'
            error_msg_email_exist = 'Email ja cadastrado'
            error_msg_password_match = 'Senhas nao conferem'
            error_msg_password_short = 'Sua senha precisa de pelo menos 6 caracteres'
            error_msg_required = 'Campo obrigatorio'


            #usuario exist
            if self.usuario:
                if usuario_db:
                    if usuario_data != usuario_db.username:
                        validation_error_msg['username'] = error_msg_user_exist

                if email_db:
                    if email_data != email_db.email:
                        validation_error_msg['email'] = error_msg_email_exist

                if password_data and password2_data:
                    if password_data != password2_data:
                        validation_error_msg['password'] = error_msg_password_match

                if password_data:
                    if len(password_data) < 6:
                        validation_error_msg['password'] = error_msg_password_short
            
            #usuario nao logados
            else:
                if usuario_db:
                    validation_error_msg['username'] = error_msg_user_exist

                if email_db:
                    validation_error_msg['email'] = error_msg_email_exist

                if not password_data:
                    validation_error_msg['password'] = error_msg_required

                if not password2_data:
                    validation_error_msg['password2'] = error_msg_required

                if password_data and password2_data:
                    if password_data != password2_data:
                        validation_error_msg['password'] = error_msg_password_match

                if password_data:
                    if len(password_data) < 6:
                        validation_error_msg['password'] = error_msg_password_short
                        
            if validation_error_msg:
                raise forms.ValidationError(validation_error_msg)

          