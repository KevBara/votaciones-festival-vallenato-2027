
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Opcion


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
        help_texts = {
            "username": "Obligatorio. Máximo 150 caracteres.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "autocomplete": "off",
            })
        self.fields["username"].widget.attrs["autocomplete"] = "username"
        self.fields["email"].widget.attrs["autocomplete"] = "email"
        self.fields["first_name"].widget.attrs["autocomplete"] = "given-name"
        self.fields["last_name"].widget.attrs["autocomplete"] = "family-name"
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password1"].help_text = (
            "La contraseña debe tener al menos 8 caracteres, no ser una "
            "contraseña de uso común ni estar compuesta solo por números."
        )
        self.fields["password2"].help_text = (
            "Escribe nuevamente la contraseña para confirmarla."
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este correo electrónico ya está registrado."
            )

        return email


class VotoForm(forms.Form):
    opcion = forms.ModelChoiceField(
        queryset=Opcion.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Selecciona tu opción"
    )

    def __init__(self, *args, votacion, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opcion"].queryset = votacion.opciones.all()
