from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db, limiter
from models import SubscriptionPlan, Subscription, Payment, PlanType, SubscriptionStatus, PaymentStatus
from services import SubscriptionService, PaymentService
import logging

logger = logging.getLogger(__name__)

@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans"""
    try:
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200

    except Exception as e:
        logger.error(f"Get plans error: {str(e)}")
        return jsonify({'error': 'Failed to get plans'}), 500

@app.route('/api/subscriptions/subscribe', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def subscribe():
    """Subscribe to a plan"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        subscription = SubscriptionService.create_subscription(
            user_id=current_user_id,
            plan_id=data['plan_id'],
            billing_cycle=data.get('billing_cycle', 'monthly'),
            payment_method=data.get('payment_method', 'stripe'),
            payment_details=data.get('payment_details', {})
        )

        db.session.commit()
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': subscription.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Subscribe error: {str(e)}")
        return jsonify({'error': 'Failed to create subscription'}), 500

@app.route('/api/subscriptions/current', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get current user subscription"""
    try:
        current_user_id = get_jwt_identity()

        subscription = Subscription.query.filter_by(
            user_id=current_user_id,
            status=SubscriptionStatus.ACTIVE
        ).first()

        if not subscription:
            return jsonify({'subscription': None}), 200

        return jsonify({'subscription': subscription.to_dict()}), 200

    except Exception as e:
        logger.error(f"Get current subscription error: {str(e)}")
        return jsonify({'error': 'Failed to get subscription'}), 500

@app.route('/api/subscriptions/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel current subscription"""
    try:
        current_user_id = get_jwt_identity()

        result = SubscriptionService.cancel_subscription(current_user_id)
        db.session.commit()

        return jsonify({
            'message': 'Subscription cancelled successfully',
            'cancelled_at': result['cancelled_at']
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Cancel subscription error: {str(e)}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500

@app.route('/api/payments/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get user's payment history"""
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        payments = Payment.query.filter_by(user_id=current_user_id)\
                               .order_by(Payment.created_at.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'payments': [payment.to_dict() for payment in payments.items],
            'total': payments.total,
            'pages': payments.pages,
            'current_page': payments.page
        }), 200

    except Exception as e:
        logger.error(f"Get payment history error: {str(e)}")
        return jsonify({'error': 'Failed to get payment history'}), 500

@app.route('/api/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')

        PaymentService.handle_stripe_webhook(payload, sig_header)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 400