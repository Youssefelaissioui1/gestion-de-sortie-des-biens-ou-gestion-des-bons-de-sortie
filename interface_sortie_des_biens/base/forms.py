from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import BonSortie, CustomUser


class BonSortieForm(forms.ModelForm):
    class Meta:
        model = BonSortie
        fields = '__all__'
        widgets = {
            'date_sortie': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat()  # empêche les dates passées
            }),
            'date_retour': forms.DateInput(attrs={'type': 'date'}),
            'objet': forms.Textarea(attrs={'rows': 6}),
            'quantite': forms.Textarea(attrs={'rows': 3}),  # Quantité multiligne
            'sn': forms.Textarea(attrs={'rows': 3}),
            'commentaire': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nature_bien'].empty_label = "— Sélectionner —"


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'code_personnel', 'type_user')


class CustomAuthenticationForm(AuthenticationForm):
    pass

from django import forms
from .models import DemandeApprobation

class DemandeApprobationAdminForm(forms.ModelForm):
    id = forms.IntegerField(required=False, disabled=True, label='ID')
    responsable_service = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(mes_groupes__nom='Responsable Service'),
        label="Responsable Service"
    )
    responsable_controlling = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(mes_groupes__nom='Responsable Controlling'),
        label="Responsable Controlling"
    )
    responsable_reception = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(mes_groupes__nom='Reception'),
        label="Responsable Réception"
    )
# .exclude(type_user='admin')
    class Meta:
        model = DemandeApprobation
        fields = ['id'] + [f.name for f in DemandeApprobation._meta.fields if f.name != 'id']
        labels = {
            'bon_sortie': 'Objet du Bon de Sortie',
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['objet'].widget = forms.HiddenInput()
        
# (Optionnel) Formulaire utilisateur, si tu en as besoin pour une vue publique
class DemandeApprobationUserForm(forms.ModelForm):
    class Meta:
        model = DemandeApprobation
        fields = ['objet',]  # ou les champs que tu veux exposer à l'utilisateur
