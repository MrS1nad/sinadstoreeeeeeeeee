from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Beat, DownloadRequest
from .forms import BeatForm, SignUpForm, DownloadRequestForm


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


def producer_list(request):
    """Публичный список всех авторов, у кого есть опубликованные биты."""
    producers = User.objects.filter(beats__is_active=True).annotate(
        beat_count=Count('beats')
    ).distinct().order_by('-beat_count')

    return render(request, 'beats/producer_list.html', {'producers': producers})


def producer_detail(request, username):
    """Публичный профиль автора со списком его битов."""
    producer = get_object_or_404(User, username=username)
    beats = Beat.objects.filter(author=producer, is_active=True)

    return render(request, 'beats/producer_detail.html', {
        'producer': producer,
        'beats': beats,
    })


def beat_list(request):
    beats = Beat.objects.filter(is_active=True)
    return render(request, 'beats/list.html', {'beats': beats})


def beat_detail(request, slug):
    """
    Страница бита. Показывает превью и форму — человек вписывает
    Telegram/телефон/почту и сразу получает файл на скачивание.
    """
    beat = get_object_or_404(Beat, slug=slug, is_active=True)
    is_author = request.user.is_authenticated and beat.author_id == request.user.id

    if request.method == 'POST':
        form = DownloadRequestForm(request.POST)
        if form.is_valid():
            download_request = form.save(commit=False)
            download_request.beat = beat
            if request.user.is_authenticated:
                download_request.user = request.user
            download_request.save()

            return FileResponse(
                beat.full_audio.open('rb'),
                as_attachment=True,
                filename=f'{beat.slug}.mp3',
            )
    else:
        form = DownloadRequestForm()

    return render(request, 'beats/detail.html', {
        'beat': beat,
        'form': form,
        'is_author': is_author,
    })


@login_required
def download_own_beat(request, slug):
    """Автор скачивает свой собственный бит без заполнения формы."""
    beat = get_object_or_404(Beat, slug=slug, author=request.user)
    return FileResponse(
        beat.full_audio.open('rb'),
        as_attachment=True,
        filename=f'{beat.slug}.mp3',
    )


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
    """Личный кабинет автора: список его битов и сколько раз каждый скачали."""
    beats = Beat.objects.filter(author=request.user).annotate(
        download_count=Count('download_requests')
    )
    return render(request, 'beats/my_beats.html', {'beats': beats})


@login_required
def beat_leads(request, slug):
    """Список контактов тех, кто скачал конкретный бит — видит только автор."""
    beat = get_object_or_404(Beat, slug=slug, author=request.user)
    leads = DownloadRequest.objects.filter(beat=beat)
    return render(request, 'beats/leads.html', {'beat': beat, 'leads': leads})
