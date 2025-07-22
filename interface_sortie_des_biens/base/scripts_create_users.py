import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interface_sortie_des_biens.settings')
django.setup()

from base.models import CustomUser, Groupe, UserType

groupes_data = [
    {"code": "SC", "label": "Service Competent"},
    {"code": "BMRT", "label": "BMRT"},
    {"code": "SCONT", "label": "Service Controlling"},
    {"code": "SMRT", "label": "SMRT"},
    {"code": "IT", "label": "Service IT"},
    {"code": "RECEP", "label": "Réception"},
]
# Créer les groupes s'ils n'existent pas
for g in groupes_data:
    Groupe.objects.get_or_create(code=g["code"], defaults={"label": g["label"]})

users = [
    # Service Competent (admin)
    {"username": "ghzi1002", "first_name": "Zineb", "last_name": "Ghamraoui", "code_personnel": "ghzi1002", "email": "ghzi1002@example.com", "groupes": ["SC"], "type_user": UserType.ADMIN, "is_staff": True, "is_superuser": True},
    {"username": "azas5002", "first_name": "Asmae", "last_name": "Aziaz", "code_personnel": "azas5002", "email": "azas5002@example.com", "groupes": ["SC"], "type_user": UserType.ADMIN, "is_staff": True, "is_superuser": True},
    {"username": "elab5010", "first_name": "Abdelghani", "last_name": "Elkhotri", "code_personnel": "elab5010", "email": "elab5010@example.com", "groupes": ["SC"], "type_user": UserType.ADMIN, "is_staff": True, "is_superuser": True},
    {"username": "boab5001", "first_name": "Abdennaji", "last_name": "Bourd", "code_personnel": "boab5001", "email": "boab5001@example.com", "groupes": ["SC"], "type_user": UserType.ADMIN, "is_staff": True, "is_superuser": True},
    {"username": "laah5001", "first_name": "Ahmed", "last_name": "Lahmar", "code_personnel": "laah5001", "email": "laah5001@example.com", "groupes": ["SC"], "type_user": UserType.ADMIN, "is_staff": True, "is_superuser": True},
    # BMRT
    {"username": "hoyo1001", "first_name": "Youness", "last_name": "Houari", "code_personnel": "hoyo1001", "email": "hoyo1001@example.com", "groupes": ["BMRT"], "type_user": UserType.NORMALE, "is_staff": False, "is_superuser": False},
    # Service Controlling
    {"username": "aias1001", "first_name": "Asmaa", "last_name": "Ait Taleb", "code_personnel": "aias1001", "email": "aias1001@example.com", "groupes": ["SCONT"], "type_user": UserType.NORMALE, "is_staff": False, "is_superuser": False},
    {"username": "jasa5001", "first_name": "Sara", "last_name": "Jaoui", "code_personnel": "jasa5001", "email": "jasa5001@example.com", "groupes": ["SCONT"], "type_user": UserType.NORMALE, "is_staff": False, "is_superuser": False},
    {"username": "medo1002", "first_name": "Dounia", "last_name": "Merhni", "code_personnel": "medo1002", "email": "medo1002@example.com", "groupes": ["SCONT"], "type_user": UserType.NORMALE, "is_staff": False, "is_superuser": False},
    # SMRT
    {"username": "taam1001", "first_name": "Amina", "last_name": "Tahiri", "code_personnel": "taam1001", "email": "taam1001@example.com", "groupes": ["SMRT"], "type_user": UserType.NORMALE, "is_staff": False, "is_superuser": False},
    # Service IT
    {"username": "ituser1", "first_name": "Ali", "last_name": "IT", "code_personnel": "ituser1", "email": "ituser1@example.com", "groupes": ["IT"], "type_user": UserType.NORMALE, "is_staff": False, "is_superuser": False},
    # Réception
    {"username": "recep1", "first_name": "Samira", "last_name": "Reception", "code_personnel": "recep1", "email": "recep1@example.com", "groupes": ["RECEP"], "type_user": UserType.NORMALE, "is_staff": False, "is_superuser": False},
]

for u in users:
    if not CustomUser.objects.filter(username=u["username"]).exists() and not CustomUser.objects.filter(code_personnel=u["code_personnel"]).exists():
        user = CustomUser.objects.create_user(
            username=u["username"],
            first_name=u["first_name"],
            last_name=u["last_name"],
            code_personnel=u["code_personnel"],
            email=u["email"],
            type_user=u["type_user"],
            is_staff=u["is_staff"],
            is_superuser=u["is_superuser"]
        )
        user.set_password(u["code_personnel"])
        user.save()
        for code in u["groupes"]:
            groupe = Groupe.objects.get(code=code)
            user.groupes.add(groupe)
        print("Utilisateur créé :", user.username)
    else:
        print("Ce username ou code_personnel existe déjà :", u["username"], u["code_personnel"])