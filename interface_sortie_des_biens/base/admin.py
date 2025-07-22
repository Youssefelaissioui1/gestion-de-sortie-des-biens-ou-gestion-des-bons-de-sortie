from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import DemandeApprobationAdminForm
from .models import CustomUser, BonSortie, DemandeApprobation, Groupe

from django.contrib import admin
from .models import Groupe
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'users_list')
    filter_horizontal = ('users',)  # Affiche un widget de sélection multiple

    def users_list(self, obj):
        return ", ".join([user.username for user in obj.users.all()])
    users_list.short_description = "Utilisateurs"

from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username','full_name', 'email', 'code_personnel', 'type_user', 'groupes_list')
    list_filter = ('type_user', 'mes_groupes__nom')
    search_fields = ('username', 'email', 'code_personnel', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'code_personnel', 'type_user')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def groupes_list(self, obj):
        return ", ".join([g.nom for g in obj.mes_groupes.all()])
    groupes_list.short_description = "Groupes"

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

@admin.register(BonSortie)
class BonSortieAdmin(admin.ModelAdmin):
    list_display = ('id','nature_bien', 'date_sortie','date_retour','destination', 'type_autorisation', 'quantite', 'created_by')
    list_filter = ('nature_bien', 'destination', 'type_autorisation', 'date_sortie')
    search_fields = ('objet',)


 


from django import forms
from django.contrib import admin
from .models import DemandeApprobation, CustomUser

from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from .models import DemandeApprobation, BonSortie

from django.contrib import admin
from base.models import DemandeApprobation
from base.forms import DemandeApprobationAdminForm
@admin.register(DemandeApprobation)
class DemandeApprobationAdmin(admin.ModelAdmin):
    form = DemandeApprobationAdminForm

    list_display = (
        'id', 'objet', 'lien_bon_sortie', 'demandeur',
        'responsable_service', 'responsable_controlling', 'responsable_reception',
        'statut_responsable_service', 'statut_responsable_controlling', 'statut_responsable_reception',
        'date_demande', 'is_retourne', 'email_envoye', 'last_reminder_sent',
    )
    list_filter = (
        'date_demande', 'statut_responsable_service', 'statut_responsable_controlling', 'statut_responsable_reception',
    )
    search_fields = (
        'objet', 'demandeur__username', 'responsable_service__username'
    )

    readonly_fields = ('display_id',)

    # Affiche display_id + tous les autres champs sauf 'id'
    def get_fields(self, request, obj=None):
        fields = ['display_id'] + [f.name for f in DemandeApprobation._meta.fields if f.name != 'id']
        return fields

    def display_id(self, obj):
        if obj and obj.pk:
            return f"ID : {obj.pk}"
        return "ID : (nouvelle demande)"
    display_id.short_description = "Identifiant"

    def lien_bon_sortie(self, obj):
        bon = obj.bon_sortie
        if bon:
            url = reverse("admin:base_bonsortie_change", args=[bon.id])
            return format_html('<a href="{}" target="_blank">Bon #{}</a>', url, bon.id)
        return "Aucun bon"
    lien_bon_sortie.short_description = "Bon de sortie lié"
