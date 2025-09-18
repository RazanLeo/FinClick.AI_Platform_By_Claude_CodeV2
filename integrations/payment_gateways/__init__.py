"""
Payment Gateways Integration Package
Provides unified access to all payment gateway services for FinClick.AI platform
"""

from .stripe_service import StripeService, create_stripe_service, format_amount_for_stripe, format_amount_from_stripe
from .paypal_service import PayPalService, PayPalEnvironment, create_paypal_service
from .paytabs_service import PayTabsService, PayTabsEnvironment, create_paytabs_service, format_phone_number
from .apple_google_pay_service import (
    ApplePayService,
    GooglePayService,
    DigitalWalletManager,
    PaymentMethod,
    create_digital_wallet_manager,
    detect_payment_method,
    get_payment_method_config
)

__all__ = [
    # Stripe
    'StripeService',
    'create_stripe_service',
    'format_amount_for_stripe',
    'format_amount_from_stripe',

    # PayPal
    'PayPalService',
    'PayPalEnvironment',
    'create_paypal_service',

    # PayTabs
    'PayTabsService',
    'PayTabsEnvironment',
    'create_paytabs_service',
    'format_phone_number',

    # Apple Pay / Google Pay
    'ApplePayService',
    'GooglePayService',
    'DigitalWalletManager',
    'PaymentMethod',
    'create_digital_wallet_manager',
    'detect_payment_method',
    'get_payment_method_config'
]