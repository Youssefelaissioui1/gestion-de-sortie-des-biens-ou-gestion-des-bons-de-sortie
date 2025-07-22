from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


from django.db import models
from django.conf import settings

class Groupe(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="mes_groupes")

    def __str__(self):
        return self.nom

# Groupes à créer :
# - Service Compétent
# - BMRT
# - Service Controlling
# - SMRT

class UserType(models.TextChoices):
    ADMIN = "admin", "Admin"
    NORMALE = "utilisateur ", "utilisateur"


class CustomUser(AbstractUser):
    code_personnel = models.CharField(max_length=30, unique=True)
    type_user = models.CharField(max_length=27, choices=UserType.choices, default=UserType.NORMALE)

    def __str__(self):
        return f"{self.get_full_name()} ({self.code_personnel})"


class BonSortie(models.Model):
    NATURE_BIENS_CHOICES = [
        ('Matière', 'Matière'),
        ('Matériels informatiques', 'Matériels informatiques'),
    ]

    DESTINATION_CHOICES = [
        ('BOK', 'BOK'),
        ('MA9', 'MA9'),
        ('BOS', 'BOS'),
        ('MA5', 'MA5'),
        ('MA7', 'MA7'),
        ('MA8', 'MA8'),
        ('AS1', 'AS1'),
        ('AS2', 'AS2'),
        ('AS3', 'AS3'),
        ('MAG', 'MAG'),
    ]

    AUTORISATION_CHOICES = [
        ('Avec Retour', 'Avec Retour'),
        ('Deplacement', 'Deplacement'),
        ('Sans Retour', 'Sans Retour'),
    ]
    nature_bien = models.CharField(max_length=100, choices=NATURE_BIENS_CHOICES)
    destination = models.CharField(max_length=100, choices=DESTINATION_CHOICES)
    type_autorisation = models.CharField(max_length=100, choices=AUTORISATION_CHOICES)

    date_sortie = models.DateField(null=False, blank=False)
    date_retour = models.DateField(null=True, blank=True)

    objet = models.TextField(null=False, blank=False)
    quantite = models.PositiveIntegerField(null=False, blank=False)

    numero_plombe = models.CharField(max_length=100, blank=True)
    sn = models.CharField("Numéro de série", max_length=100, blank=True)

    commentaire = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='bons_sortie_crees')

    def __str__(self):
        parts = [f"Bon id {self.id} - {self.nature_bien} - de objet : {self.objet} "]

        if self.sn:
            parts.append(f"SN: {self.sn}")
        if self.numero_plombe:
            parts.append(f"Numero Plombe: {self.numero_plombe}")

        return " | ".join(parts)




    class Meta:
        ordering = ['-id']  # Trie par ID décroissant

class DemandeApprobation(models.Model):
    STATUT_CHOICES = [
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('accepted', 'accepted'),
        ('rejected', 'Rejected'),
    ]

    bon_sortie = models.ForeignKey(BonSortie, on_delete=models.CASCADE)
    objet = models.TextField()
    demandeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    responsable_service = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='service_approbations', on_delete=models.CASCADE)
    responsable_controlling = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='controlling_approbations', on_delete=models.CASCADE)
    responsable_reception = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reception_approbations', on_delete=models.CASCADE)

    date_demande = models.DateTimeField(default=timezone.now)

    statut_responsable_service = models.CharField(max_length=30, choices=STATUT_CHOICES, default='pending')
    statut_responsable_controlling = models.CharField(max_length=30, choices=STATUT_CHOICES, default='not_started')
    statut_responsable_reception = models.CharField(max_length=30, choices=STATUT_CHOICES, default='not_started')
    is_retourne = models.BooleanField(default=False, help_text="Cocher si le bien a été retourné.")
    email_envoye = models.BooleanField(default=False) 
    last_reminder_sent = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Demande #{self.id} - Bon #{self.bon_sortie.id} par {self.demandeur}"


    def statut_global(self):
        # Si un seul responsable a rejeté, le produit est rejeté
        if 'rejected' in [self.statut_responsable_service, self.statut_responsable_controlling, self.statut_responsable_reception]:
            return 'rejected'
        # Sinon si réception accepté, produit prêt
        elif self.statut_responsable_reception == 'accepted':
            return 'accepted'
        # Sinon en attente
        else:
            return 'pending'
