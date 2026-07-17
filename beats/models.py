import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Beat(models.Model):
    """Один бит с обложкой, превью и полным аудиофайлом."""

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=220, unique=True, blank=True)
    description = models.TextField('Описание', blank=True)
    bpm = models.PositiveIntegerField('BPM', blank=True, null=True)
    genre = models.CharField('Жанр', max_length=100, blank=True)

    cover = models.ImageField('Обложка', upload_to='covers/')

    # Короткое превью, которое можно слушать бесплатно (например, 30-60 сек, с тегом)
    preview_audio = models.FileField('Превью (для прослушивания)', upload_to='audio_previews/')

    # Полный трек без тегов — открывается только после оплаты
    full_audio = models.FileField('Полный файл (после покупки)', upload_to='audio_full/')

    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
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


class Purchase(models.Model):
    """Покупка бита конкретным пользователем."""

    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает оплаты'),
        (STATUS_PAID, 'Оплачено'),
        (STATUS_FAILED, 'Ошибка оплаты'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE, related_name='purchases')

    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    amount = models.DecimalField('Сумма', max_digits=8, decimal_places=2)

    # Идентификатор сессии/платежа во внешней платёжной системе
    payment_session_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField('Создана', auto_now_add=True)
    paid_at = models.DateTimeField('Оплачена', blank=True, null=True)

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'beat'],
                condition=models.Q(status='paid'),
                name='unique_paid_purchase_per_user_beat',
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.beat} ({self.status})'
