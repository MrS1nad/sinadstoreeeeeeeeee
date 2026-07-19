import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Beat(models.Model):
    """Один бит с обложкой, превью и полным аудиофайлом."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='beats',
        verbose_name='Автор',
    )
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=220, unique=True, blank=True)
    description = models.TextField('Описание', blank=True)
    bpm = models.PositiveIntegerField('BPM', blank=True, null=True)
    genre = models.CharField('Жанр', max_length=100, blank=True)

    cover = models.ImageField('Обложка', upload_to='covers/')

    # Короткое превью, которое можно слушать бесплатно (например, 30-60 сек, с тегом)
    preview_audio = models.FileField('Превью (для прослушивания)', upload_to='audio_previews/')

    # Полный трек без тегов — открывается после того, как человек оставит контакты
    full_audio = models.FileField('Полный файл (для скачивания)', upload_to='audio_full/')

    is_active = models.BooleanField('Опубликован', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Бит'
        verbose_name_plural = 'Биты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or uuid.uuid4().hex[:8]
            slug = base_slug
            n = 1
            while Beat.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base_slug}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('beat_detail', args=[self.slug])


class DownloadRequest(models.Model):
    """
    Заявка на скачивание бита. Вместо оплаты человек оставляет контакты —
    так автор бита может сам связаться с покупателем и договориться об условиях.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE, related_name='download_requests')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='download_requests',
        blank=True,
        null=True,
        help_text='Если человек был залогинен в момент скачивания',
    )

    name = models.CharField('Имя', max_length=150, blank=True)
    telegram = models.CharField('Telegram', max_length=150)
    phone = models.CharField('Телефон', max_length=50)
    email = models.EmailField('Email')

    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на скачивание'
        verbose_name_plural = 'Заявки на скачивание'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.telegram or self.email} -> {self.beat}'
