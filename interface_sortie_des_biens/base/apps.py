from django.apps import AppConfig
import threading
import time
import os

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        from base.tasks import verifier_et_envoyer_rappels

        # Pour éviter les multiples threads dans le reloader
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        def start_reminder_loop():
            print("🚀 Rappel automatique toutes les 5 minutes activé.")
            while True:
                verifier_et_envoyer_rappels()
                time.sleep(300)  # 300 secondes = 5 minutes

        t = threading.Thread(target=start_reminder_loop, daemon=True)
        t.start()
