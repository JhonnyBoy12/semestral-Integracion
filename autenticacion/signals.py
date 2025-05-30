from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from inventario.models import Profile


@receiver(post_save, sender=User)
def crear_token_usuario(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)