from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Beat, Purchase
from .forms import BeatForm, SignUpForm
from . import payments


def signup(request):
    """Регистрация нового пользователя, доступна всем."""
    if request.user.is_authenticated:
        return redirect('beat_list')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'beat_list'
            return redirect(next_url)
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


def beat_list(request):
    beats = Beat.objects.filter(is_active=True)
    return render(request, 'beats/list.html', {'beats': beats})


def beat_detail(request, slug):
    beat = get_object_or_404(Beat, slug=slug, is_active=True)

    already_purchased = False
    is_author = False
    if request.user.is_authenticated:
        is_author = beat.author_id == request.user.id
        already_purchased = is_author or Purchase.objects.filter(
            user=request.user, beat=beat, status=Purchase.STATUS_PAID
        ).exists()

    return render(request, 'beats/detail.html', {
        'beat': beat,
        'already_purchased': already_purchased,
        'is_author': is_author,
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
def upload_beat(request):
    """Форма, через которую любой залогиненный пользователь выкладывает свой бит."""
    if request.method == 'POST':
        form = BeatForm(request.POST, request.FILES)
        if form.is_valid():
            beat = form.save(commit=False)
            beat.author = request.user
            beat.save()
            messages.success(request, f'Бит «{beat.title}» опубликован.')
            return redirect('beat_detail', slug=beat.slug)
    else:
        form = BeatForm()

    return render(request, 'beats/upload_form.html', {'form': form, 'is_edit': False})


@login_required
def edit_beat(request, slug):
    """Редактирование бита — доступно только автору."""
    beat = get_object_or_404(Beat, slug=slug, author=request.user)

    if request.method == 'POST':
        form = BeatForm(request.POST, request.FILES, instance=beat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены.')
            return redirect('beat_detail', slug=beat.slug)
    else:
        form = BeatForm(instance=beat)

    return render(request, 'beats/upload_form.html', {'form': form, 'is_edit': True, 'beat': beat})


@login_required
def delete_beat(request, slug):
    """Удаление бита — доступно только автору, подтверждение обязательно."""
    beat = get_object_or_404(Beat, slug=slug, author=request.user)

    if request.method == 'POST':
        title = beat.title
        beat.delete()
        messages.success(request, f'Бит «{title}» удалён.')
        return redirect('my_beats')

    return render(request, 'beats/delete_confirm.html', {'beat': beat})


@login_required
def my_beats(request):
    """Личный кабинет автора со списком его битов и статистикой продаж."""
    beats = Beat.objects.filter(author=request.user).annotate(
        sales_count=Count('purchases', filter=Q(purchases__status=Purchase.STATUS_PAID))
    )
    return render(request, 'beats/my_beats.html', {'beats': beats})


@login_required
def download_beat(request, slug):
    """Отдаёт полный файл только тем, кто реально оплатил."""
    beat = get_object_or_404(Beat, slug=slug)

    is_author = beat.author_id == request.user.id
    purchased = is_author or Purchase.objects.filter(
        user=request.user, beat=beat, status=Purchase.STATUS_PAID
    ).exists()

    if not purchased:
        raise Http404('Покупка не найдена')

    return FileResponse(
        beat.full_audio.open('rb'),
        as_attachment=True,
        filename=f'{beat.slug}.mp3',
    )
