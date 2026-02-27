"""
Tâches Celery : alertes SMS via Brevo.
"""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def send_sms_repas(self, message: str, telephone: str):
    """Envoie un SMS via l'API REST Brevo (httpx)."""
    try:
        import httpx
        from meals.models import Config

        config = Config.get()
        if not config.sms_actif or not config.brevo_api_key:
            logger.info('SMS désactivé ou clé API manquante.')
            return

        response = httpx.post(
            'https://api.brevo.com/v3/transactionalSMS/sms',
            headers={
                'api-key': config.brevo_api_key,
                'content-type': 'application/json',
            },
            json={
                'sender': 'FamilyMeal',
                'recipient': telephone,
                'content': message,
                'type': 'transactional',
            },
            timeout=15,
        )
        response.raise_for_status()
        logger.info(f'SMS envoyé à {telephone}: {message}')
    except Exception as exc:
        logger.error(f'Erreur envoi SMS à {telephone}: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task
def verifier_et_envoyer_alertes():
    """
    Tâche périodique : vérifie si un repas est prévu dans les 2 prochaines heures
    et envoie les alertes SMS aux membres concernés.
    Doit être appelée toutes les 5-10 minutes via Celery Beat.
    """
    from django.utils import timezone
    from datetime import timedelta
    from meals.models import Config, SemaineMenu, CreneauPlanning, Membre

    now = timezone.localtime()
    config = Config.get()

    if not config.sms_actif:
        return

    # Chercher les créneaux du planning publié pour aujourd'hui
    aujourd_hui = now.date()
    semaines = SemaineMenu.objects.filter(statut='publie')
    if not semaines.exists():
        return

    membres = list(Membre.objects.filter(actif=True, telephone__gt=''))

    for creneau_obj in CreneauPlanning.objects.filter(
        semaine__statut='publie',
        date=aujourd_hui,
        plat_principal__isnull=False,
    ).select_related('plat_principal', 'plat_secours'):

        heure_repas = (
            config.heure_midi if creneau_obj.creneau == 'midi' else config.heure_soir
        )

        # Construire le datetime du repas en heure locale
        repas_dt = timezone.make_aware(
            timezone.datetime.combine(aujourd_hui, heure_repas)
        )

        delta = (repas_dt - now).total_seconds()

        # Envoyer si le repas est dans la fenêtre [1h45 – 2h15]
        if 6300 <= delta <= 8100:  # 105–135 minutes
            plat_nom = creneau_obj.plat_principal.nom
            moment = 'CE MIDI' if creneau_obj.creneau == 'midi' else 'CE SOIR'

            # Message de base
            message_base = f"Le repas de {moment} est : {plat_nom}"

            # Ajouter info plat de secours si pertinent
            membres_secours_ids = set(
                creneau_obj.membres_secours.values_list('id', flat=True)
            )

            for membre in membres:
                if membre.id in membres_secours_ids and creneau_obj.plat_secours:
                    msg = f"{message_base} (ou {creneau_obj.plat_secours.nom} pour toi)"
                else:
                    msg = message_base

                send_sms_repas.delay(msg, membre.telephone)

    logger.info(f'Vérification alertes repas effectuée à {now.strftime("%H:%M")}')


@shared_task
def programmer_alertes_semaine(semaine_id: int):
    """
    Appelé quand un planning est publié.
    Configure la tâche périodique dans Celery Beat si elle n'existe pas déjà.
    """
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    import json

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=5,
        period=IntervalSchedule.MINUTES,
    )
    PeriodicTask.objects.get_or_create(
        name='verifier-alertes-repas',
        defaults={
            'interval': schedule,
            'task': 'meals.tasks.verifier_et_envoyer_alertes',
            'args': json.dumps([]),
        },
    )
    logger.info(f'Tâche périodique alertes activée pour semaine {semaine_id}')
