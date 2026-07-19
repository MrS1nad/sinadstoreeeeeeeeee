"""
Слой оплаты. Здесь используется Stripe как пример, потому что у него
самая понятная документация и тестовый режим без реального банка.

Если тебе нужна оплата картами РФ — замени содержимое функций
create_checkout_session() и handle_webhook() на вызовы ЮKassa /
CloudPayments / Robokassa. Сигнатуры функций (что они принимают
и что возвращают) можно оставить такими же, тогда views.py менять
не придётся.
"""

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(purchase, request):
    """
    Создаёт сессию оплаты во внешней системе и возвращает URL,
    на который нужно перенаправить покупателя.
    """
    success_url = request.build_absolute_uri(
        f'/purchase/{purchase.id}/success/'
    ) + '?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = request.build_absolute_uri(f'/beat/{purchase.beat.slug}/')

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',  # для рублей используй 'rub', если поддерживается аккаунтом
                'product_data': {
                    'name': purchase.beat.title,
                },
                'unit_amount': int(purchase.amount * 100),  # в минимальных единицах валюты
            },
            'quantity': 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(purchase.id),
    )

    purchase.payment_session_id = session.id
    purchase.save(update_fields=['payment_session_id'])

    return session.url


def verify_session_paid(session_id):
    """Проверяет у платёжной системы, действительно ли сессия оплачена."""
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status == 'paid'
