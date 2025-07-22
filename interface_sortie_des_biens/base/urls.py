from django.urls import path
from . import views

urlpatterns = [
    path('', views.connexion, name='connexion'),
    path('Add_Bon_Sortie/', views.nouveau_bon, name='nouveau_bon'),
    path('all/', views.allBonSortie, name='allBonSortie'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('demander_approbation/<int:id>/', views.demander_approbation, name='demander_approbation'),
    path('demandes/', views.liste_demandes, name='liste_demandes'),
    path('demande/<int:demande_id>/<str:role>/changer-statut/', views.changer_statut, name='changer_statut'),
    path('changer_statut_retour/<int:demande_id>/', views.changer_statut_retour, name='changer_statut_retour'),
    path('demande/<int:demande_id>/', views.detail_demande, name='detail_demande'),
    path('mot-de-passe-oublie/', views.forgot_password_view, name='forgot_password'),
    path('forgot-password/reset/', views.reset_forgot_password_session, name='reset_forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),


]
