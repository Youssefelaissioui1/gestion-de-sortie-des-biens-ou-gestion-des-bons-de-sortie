from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from collections import defaultdict
from base.models import DemandeApprobation

def verifier_et_envoyer_rappels():
    today = timezone.now().date()

    demandes = DemandeApprobation.objects.filter(
        bon_sortie__date_retour__lt=today,
        is_retourne=False,
        statut_responsable_service='accepted',
        statut_responsable_controlling='accepted',
        statut_responsable_reception='accepted',
    )

    demandes_par_responsable = defaultdict(list)
    for demande in demandes:
        if demande.responsable_reception:
            demandes_par_responsable[demande.responsable_reception].append(demande)

    print(f"📢 {demandes.count()} bons en retard ! Envoi des emails...")

    for responsable, demandes_list in demandes_par_responsable.items():
        lignes_texte = []
        lignes_html = []

        for demande in demandes_list:
            lien = f"{settings.SITE_URL}{reverse('changer_statut_retour', args=[demande.id])}"
            lignes_texte.append(
                f"Bon #{demande.id}, retour prévu avant le {demande.bon_sortie.date_retour} - Finaliser le retour : {lien}"
            )
            lignes_html.append(
                f'<li style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px;">'
                f'<div style="font-size: 17px; color: #2c3e50; margin-bottom: 8px;">'
                f'<strong>Bon #{demande.id}</strong> — retour avant <strong>{demande.bon_sortie.date_retour}</strong>'
                f'</div>'
                f'<a href="{lien}" '
                f'style="display: inline-block; background-color: #007bff; color: white; text-decoration: none; padding: 10px 20px; '
                f'border-radius: 5px; font-weight: 600; font-size: 15px;">📄 Finaliser le retour</a>'
                f'</li>'
            )

        sujet = "[Rappel] Bons de sortie non retournés"
        destinataires = [responsable.email]

        corps_texte = (
            f"Bonjour {responsable.first_name},\n\n"
            "Vous avez les bons de sortie suivants qui n'ont pas encore été retournés :\n\n"
            + "\n".join(lignes_texte) +
            "\n\nMerci de finaliser ces retours.\n\nCordialement,\nL'équipe de gestion"
        )

        corps_html = f"""
        <html>
          <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; padding: 30px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
              <h2 style="color: #2c3e50; margin-bottom: 25px;">🔔 Rappel : Bons de sortie en attente de retour</h2>
              <p style="font-size: 16px; color: #34495e; line-height: 1.5;">
                Bonjour <strong>{responsable.first_name} {responsable.last_name}</strong>,<br><br>
                Nous vous rappelons que les bons de sortie listés ci-dessous n'ont pas encore été retournés, bien que la date limite soit dépassée.
              </p>
              <ul style="list-style: none; padding-left: 0;">
                {''.join(lignes_html)}
              </ul>
              <p style="font-size: 16px; color: #34495e; line-height: 1.5; margin-top: 30px;">
                Merci de procéder à la finalisation de ces retours dans les meilleurs délais afin de garantir la bonne gestion des biens.
              </p>
              <p style="font-size: 16px; color: #34495e; line-height: 1.5;">
                Cordialement,<br>
                <strong>Service IT</strong>
              </p>
            </div>
          </body>
        </html>
        """

        email = EmailMultiAlternatives(
            sujet, corps_texte, settings.DEFAULT_FROM_EMAIL, destinataires
        )
        email.attach_alternative(corps_html, "text/html")
        email.send()

        print(f"✅ Email envoyé à {responsable.email} avec {len(demandes_list)} bon(s) de demande ID #{demande.id} à {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
