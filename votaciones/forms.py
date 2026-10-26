
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Correo electrónico"
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre"
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Apellido"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

        labels = {
            "username": "Nombre de usuario",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este correo electrónico ya está registrado."
            )

        return email
