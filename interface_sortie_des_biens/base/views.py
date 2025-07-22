import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from .forms import BonSortieForm, CustomAuthenticationForm
from .models import BonSortie, DemandeApprobation, CustomUser

User = get_user_model()  # Modèle utilisateur personnalisé


@login_required
def nouveau_bon(request):
    if request.method == 'POST':
        form = BonSortieForm(request.POST)
        if form.is_valid():
            bon = form.save(commit=False)
            bon.created_by = request.user
            bon.save()
            messages.success(request, "Bon créé avec succès !")
            return redirect('demander_approbation', id=bon.id)
    else:
        form = BonSortieForm()
    return render(request, 'bon_form.html', {'form': form})


@login_required
def allBonSortie(request):
    all_bons = BonSortie.objects.all().order_by('-id')  # ou '-created_at' si dispo
    bons_avec_demande = DemandeApprobation.objects.values_list('bon_sortie_id', flat=True).distinct()

 
    return render(request, 'all_bon_sortie.html', {'bons': all_bons, 'bons_avec_demande': set(bons_avec_demande),  # converti en set pour accès rapide
})



def connexion(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or 'allBonSortie'
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'connexion.html', {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    return redirect('connexion')


def envoyer_email_utilisateur(user, sujet, message_corps):
    if not user.email:
        print(f"L'utilisateur {user} n'a pas d'email, email non envoyé.")
        return
    send_mail(
        sujet,
        message_corps,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from base.models import BonSortie, DemandeApprobation, CustomUser
from base.forms import DemandeApprobationUserForm

@login_required
def demander_approbation(request, id):
    bon = get_object_or_404(BonSortie, id=id)
    
    objet_default = bon.objet

    if request.method == 'POST':
        form = DemandeApprobationUserForm(request.POST)

        if form.is_valid():
            # Récupérer les emails des responsables via POST
            email_service = request.POST.get('responsable_service')
            email_controlling = request.POST.get('responsable_controlling')
            email_reception = request.POST.get('responsable_reception')

            # Vérifier que tous les emails sont présents
            if not email_service or not email_controlling or not email_reception:
                messages.error(request, "Tous les responsables doivent être sélectionnés.")
            else:
                # Convertir les emails en objets CustomUser
                respo_service = CustomUser.objects.filter(email=email_service).first()
                respo_controlling = CustomUser.objects.filter(email=email_controlling).first()
                respo_reception = CustomUser.objects.filter(email=email_reception).first()

                # Vérifier que tous les utilisateurs existent
                if not all([respo_service, respo_controlling, respo_reception]):
                    messages.error(request, "Un ou plusieurs emails sont invalides ou les utilisateurs n’existent pas.")
                else:
                    # Vérifier s'il y a déjà une demande pour ce bon
                    demande_existante = DemandeApprobation.objects.filter(bon_sortie=bon).exists()
                    if demande_existante:
                        messages.warning(request, "Une demande d’approbation a déjà été soumise pour ce bon.")
                    else:
                        # Créer la demande
                        demande = DemandeApprobation.objects.create(
                            bon_sortie=bon,
                            objet=objet_default,
                            demandeur=request.user,
                            responsable_service=respo_service,
                            statut_responsable_service='pending',
                            responsable_controlling=respo_controlling,
                            statut_responsable_controlling='not_started',
                            responsable_reception=respo_reception,
                            statut_responsable_reception='not_started',
                            date_demande=timezone.now(),
                            is_retourne=False
                        )

                        # Générer les liens pour valider/refuser
                        lien_service = request.build_absolute_uri(reverse('changer_statut', args=[demande.id, 'service']))
                        lien_controlling = request.build_absolute_uri(reverse('changer_statut', args=[demande.id, 'controlling']))
                        lien_reception = request.build_absolute_uri(reverse('changer_statut', args=[demande.id, 'reception']))

                        # Envoyer l'email au responsable de service
                        envoyer_email_utilisateur(
                            demande.responsable_service,
                            sujet=f"Demande Bon Sortie #{demande.id} - Validation requise",
                            message_corps=f"""Bonjour {demande.responsable_service.first_name} {demande.responsable_service.last_name},

Vous avez une demande d'approbation à traiter pour le bon de sortie #{demande.bon_sortie.id}.
Cliquez ici pour valider ou refuser : {lien_service}

Merci de vous connecter avec votre compte.
"""
                        )

                        messages.success(request, "Demande d'approbation créée avec succès.")
                        return redirect('liste_demandes')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
            messages.error(request, form.errors.as_text())
    else:
        form = DemandeApprobationUserForm(initial={'objet': objet_default})

    # Préparer les listes d’utilisateurs pour le frontend
    users_service = CustomUser.objects.filter(mes_groupes__nom='Responsable Service')
    users_controlling = CustomUser.objects.filter(mes_groupes__nom='Responsable Controlling')
    users_reception = CustomUser.objects.filter(mes_groupes__nom='Reception')
    demande = DemandeApprobation.objects.filter(bon_sortie=bon).first()

    return render(request, 'demander_approbation.html', {
        'form': form,
        'objet_default': objet_default,
        'users_service': users_service,
        'users_controlling': users_controlling,
        'users_reception': users_reception,
        'demande': demande,
    })


from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import DemandeApprobation

@login_required
def liste_demandes(request):
    demandes = DemandeApprobation.objects.all().order_by('-id')
    objet = request.GET.get('objet', '').strip()
    id_sortie = request.GET.get('id_sortie', '').strip()
    id_demande = request.GET.get('id_demande', '').strip()
    date_retour = request.GET.get('date_retour', '').strip()  # <-- changé ici

    if objet:
        demandes = demandes.filter(objet__icontains=objet)

    if id_sortie:
        demandes = demandes.filter(bon_sortie__id__iexact=id_sortie)

    if id_demande:
        demandes = demandes.filter(id__iexact=id_demande)

    if date_retour:
        try:
            date_obj = datetime.strptime(date_retour, "%Y-%m-%d").date()
            demandes = demandes.filter(bon_sortie__date_retour=date_obj)  # <-- changé ici
        except ValueError:
            pass  # ignore si la date est invalide

    return render(request, 'liste_demandes.html', {'demandes': demandes})


#changer statut de responsable
def changer_statut(request, demande_id, role):
    if not request.user.is_authenticated:
        login_url = f"{reverse('connexion')}?next={request.path}"
        return render(request, 'connexion_necessaire.html', {'login_url': login_url})
    demande = get_object_or_404(DemandeApprobation, id=demande_id)
    user = request.user

    # Définir le nom du groupe attendu selon le rôle
    if role == 'service':
        groupe_requis = 'Responsable Service'
    elif role == 'controlling':
        groupe_requis = 'Responsable Controlling'
    elif role == 'reception':
        groupe_requis = 'Reception'
    else:
        groupe_requis = None

    # Vérifier si l'utilisateur appartient au groupe requis
    est_responsable = user.mes_groupes.filter(nom=groupe_requis).exists() if groupe_requis else False

    if request.method == 'POST':
        if not est_responsable:
            messages.error(request, "Vous n'êtes pas autorisé à modifier ce statut.")
            return redirect('changer_statut', demande_id=demande_id, role=role)

        decision = request.POST.get('decision')
        if decision not in ['accepted', 'rejected']:
            messages.error(request, "Décision invalide.")
            return redirect('changer_statut', demande_id=demande_id, role=role)

        # Mise à jour du statut selon le rôle
        if role == 'service':
            demande.statut_responsable_service = decision
            if decision == 'accepted':
                # Mettre le statut du controlling à 'pending'
                demande.statut_responsable_controlling = 'pending'
                # Envoyer l'email au responsable controlling
                lien_controlling = request.build_absolute_uri(
                    reverse('changer_statut', args=[demande.id, 'controlling'])
                )
                envoyer_email_utilisateur(
                    demande.responsable_controlling,
                    sujet=f"Demande Bon Sortie #{demande.id} - Validation requise (Controlling)",
                    message_corps=f"""Bonjour {demande.responsable_controlling.first_name},\n
Vous avez une demande d'approbation à traiter pour le bon de sortie #{demande.bon_sortie.id}.\n
Cliquez ici pour valider ou refuser : {lien_controlling}\n
Merci de vous connecter avec votre compte."""
                )
            else:
                # Si refusé, on peut marquer les autres statuts comme 'rejected'
                demande.statut_responsable_controlling = 'rejected'
                demande.statut_responsable_reception = 'rejected'

        elif role == 'controlling':
            demande.statut_responsable_controlling = decision
            if decision == 'accepted':
                demande.statut_responsable_reception = 'pending'
                # Envoyer l'email au responsable réception
                lien_reception = request.build_absolute_uri(
                    reverse('changer_statut', args=[demande.id, 'reception'])
                )
                envoyer_email_utilisateur(
                    demande.responsable_reception,
                    sujet=f"Demande Bon Sortie #{demande.id} - Validation requise (Réception)",
                    message_corps=f"""Bonjour {demande.responsable_reception.first_name},\n
Vous avez une demande d'approbation à traiter pour le bon de sortie #{demande.bon_sortie.id}.\n
Cliquez ici pour valider ou refuser : {lien_reception}\n
Merci de vous connecter avec votre compte."""
                )
            else:
                demande.statut_responsable_reception = 'rejected'

        elif role == 'reception':
            demande.statut_responsable_reception = decision

        demande.save()
        messages.success(request, "Statut mis à jour avec succès.")
        return redirect('liste_demandes')

    return render(request, 'changer_statut.html', {
        'demande': demande,
        'role': role,
        'est_responsable': est_responsable,
        'groupe_requis': groupe_requis,
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from base.models import DemandeApprobation

def changer_statut_retour(request, demande_id):
    if not request.user.is_authenticated:
        # Redirige vers la page de connexion avec retour à cette page après connexion
        return redirect(f"{reverse('connexion')}?next={request.path}")

    demande = get_object_or_404(DemandeApprobation, id=demande_id)

    # Vérifie que l'utilisateur est dans le groupe 'Reception'
    est_responsable = request.user.mes_groupes.filter(nom='Reception').exists()

    if request.method == 'POST':
        if not est_responsable:
            messages.error(request, "Vous n'avez pas la permission de modifier ce statut.")
            return redirect('changer_statut_retour', demande_id=demande_id)

        retour = request.POST.get('retour')
        if retour not in ['true', 'false']:
            messages.error(request, "Valeur invalide pour le retour.")
            return redirect('changer_statut_retour', demande_id=demande_id)

        # Met à jour le champ is_retourne (et non statut_retour)
        demande.is_retourne = (retour == 'true')
        demande.save()

        messages.success(request, "Statut de retour mis à jour avec succès.")
        return redirect('liste_demandes')

    return render(request, 'changer_statut_retour.html', {
        'demande': demande,
        'est_responsable': est_responsable,
    })




@login_required
def detail_demande(request, demande_id):
    demande = get_object_or_404(DemandeApprobation, id=demande_id)
    return render(request, 'detail_demande.html', {'demande': demande})




import random
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from base.models import CustomUser
def forgot_password_view(request):
    if request.method == 'POST' and 'send_code' in request.POST:
        user_email = request.POST.get('user_email')

        if not user_email:
            messages.error(request, "Veuillez saisir un email utilisateur.")
            return redirect('forgot_password')

        user_qs = CustomUser.objects.filter(email=user_email).exclude(type_user='admin')
        if not user_qs.exists():
            messages.error(request, "Email utilisateur introuvable ou utilisateur admin.")
            return redirect('forgot_password')

        user = user_qs.first()

        code = random.randint(100000, 999999)
        sujet = 'Code de réinitialisation du mot de passe'
        message_corps = f'Bonjour, voici votre code de réinitialisation : {code}'

        send_mail(
            sujet,
            message_corps,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )

        request.session['reset_code'] = str(code)
        request.session['reset_user_email'] = user_email

        messages.success(request, f'Code envoyé avec succès à {user_email}. Veuillez entrer ce code ci-dessous.')
        return redirect('forgot_password')

    elif request.method == 'POST' and 'verify_code' in request.POST:
        entered_code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not entered_code or not new_password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('forgot_password')

        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('forgot_password')

        session_code = request.session.get('reset_code')
        user_email = request.session.get('reset_user_email')

        if not session_code or not user_email:
            messages.error(request, "Aucun code envoyé ou session expirée.")
            return redirect('forgot_password')

        if entered_code != session_code:
            messages.error(request, "Code incorrect.")
            return redirect('forgot_password')

        try:
            user = CustomUser.objects.get(email=user_email)
            user.set_password(new_password)
            user.save()

            del request.session['reset_code']
            del request.session['reset_user_email']

            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect('connexion')
        except CustomUser.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
            return redirect('forgot_password')
        
        

    emails = CustomUser.objects.exclude(type_user='admin').values_list('email', flat=True).distinct()
    return render(request, 'mot_de_passe_oublie.html', {'emails': emails})



from django.contrib import messages
from django.shortcuts import redirect

def reset_forgot_password_session(request):
    # Supprime les clés en session qui gardent l’état du reset
    request.session.pop('reset_code', None)
    request.session.pop('reset_user_email', None)
    messages.info(request, "La procédure de réinitialisation a été réinitialisée.")
    return redirect('forgot_password')  # redirige vers la page principale



from datetime import datetime

def ma_vue(request):
    context = {
        'current_year': datetime.now().year,
        # autres contextes
    }
    return render(request, 'base.html', context)






import json
from django.shortcuts import render
from django.db.models import Count
from base.models import DemandeApprobation

def dashboard(request):
    demandes = DemandeApprobation.objects.all()

    # Fonction pour calculer le statut global d'une demande
    def statut_global(d):
        statuts = [
            d.statut_responsable_service,
            d.statut_responsable_controlling,
            d.statut_responsable_reception,
        ]
        if 'rejected' in statuts:
            return 'rejected'
        elif any(s in ['pending', 'not_started'] for s in statuts):
            return 'pending'
        elif all(s == 'accepted' for s in statuts):
            return 'accepted'
        else:
            return 'unknown'

    # Calcul des totaux par statut global
    total_demandes = demandes.count()
    demandes_rejetees = sum(1 for d in demandes if statut_global(d) == 'rejected')
    demandes_en_attente = sum(1 for d in demandes if statut_global(d) == 'pending')
    demandes_acceptees = sum(1 for d in demandes if statut_global(d) == 'accepted')

    # Top 5 des demandeurs les plus actifs (par full_name)
    top_demandeurs_data = (
        DemandeApprobation.objects
        .values('demandeur__first_name', 'demandeur__last_name')
        .annotate(nb=Count('id'))
        .order_by('-nb')[:11]
    )

    # Construire les labels en concaténant prénom + nom
    top_labels = [
        f"{entry['demandeur__first_name']} {entry['demandeur__last_name']}"
        for entry in top_demandeurs_data
    ]
    top_counts = [entry['nb'] for entry in top_demandeurs_data]

    context = {
        'total_demandes': total_demandes,
        'demandes_en_attente': demandes_en_attente,
        'demandes_acceptees': demandes_acceptees,
        'demandes_rejetees': demandes_rejetees,
        'top_demandeurs_labels': json.dumps(top_labels),
        'top_demandeurs_counts': json.dumps(top_counts),
    }

    return render(request, 'dashboard.html', context)
