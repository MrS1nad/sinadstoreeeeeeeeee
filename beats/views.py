from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Beat, Purchase
from . import payments


def beat_list(request):
    beats = Beat.objects.filter(is_active=True)
    return render(request, 'beats/list.html', {'beats': beats})


def beat_detail(request, slug):
    beat = get_object_or_404(Beat, slug=slug, is_active=True)

    already_purchased = False
    if request.user.is_authenticated:
        already_purchased = Purchase.objects.filter(
            user=request.user, beat=beat, status=Purchase.STATUS_PAID
        ).exists()

    return render(request, 'beats/detail.html', {
        'beat': beat,
        'already_purchased': already_purchased,
    })


@login_required
def start_purchase(request, slug):
    """Создаёт заявку на покупку и уводит пользователя на оплату."""
    beat = get_object_or_404(Beat, slug=slug, is_active=True)

    if Purchase.objects.filter(user=request.user, beat=beat, status=Purchase.STATUS_PAID).exists():
        messages.info(request, 'Ты уже купил этот бит.')
        return redirect('beat_detail', slug=beat.slug)

    purchase = Purchase.objects.create(
        user=request.user,
        beat=beat,
        amount=beat.price,
        status=Purchase.STATUS_PENDING,
    )

    checkout_url = payments.create_checkout_session(purchase, request)
    return redirect(checkout_url)


@login_required
def purchase_success(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    session_id = request.GET.get('session_id')

    if purchase.status != Purchase.STATUS_PAID and session_id:
        if payments.verify_session_paid(session_id):
            purchase.status = Purchase.STATUS_PAID
            purchase.paid_at = timezone.now()
            purchase.save(update_fields=['status', 'paid_at'])

    return render(request, 'beats/success.html', {'purchase': purchase})


@login_required
def download_beat(request, slug):
    """Отдаёт полный файл только тем, кто реально оплатил."""
    beat = get_object_or_404(Beat, slug=slug)

    purchased = Purchase.objects.filter(
        user=request.user, beat=beat, status=Purchase.STATUS_PAID
    ).exists()

    if not purchased:
        raise Http404('Покупка не найдена')

    return FileResponse(
        beat.full_audio.open('rb'),
        as_attachment=True,
        filename=f'{beat.slug}.mp3',
    )
