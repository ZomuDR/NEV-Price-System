from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

def user_avatar_path(instance, filename):
    # 头像存储路径：avatars/用户名/时间戳.扩展名
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f'avatars/{instance.username}/{timestamp}.{ext}'

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        default='default_avatar.svg'
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'