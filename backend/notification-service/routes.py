from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db, limiter
from models import Notification, NotificationTemplate, UserNotificationSettings, NotificationType, NotificationStatus
from services import NotificationService
import logging

logger = logging.getLogger(__name__)

@app.route('/api/notifications/send', methods=['POST'])
@jwt_required()
@limiter.limit("100 per hour")
def send_notification():
    """Send a notification"""
    try:
        data = request.get_json()

        notification = NotificationService.send_notification(
            user_id=data['user_id'],
            type=NotificationType(data['type']),
            title=data['title'],
            message=data['message'],
            recipient=data.get('recipient'),
            data=data.get('data', {}),
            scheduled_at=data.get('scheduled_at')
        )

        db.session.commit()
        return jsonify({
            'message': 'Notification sent successfully',
            'notification': notification.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Send notification error: {str(e)}")
        return jsonify({'error': 'Failed to send notification'}), 500

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user's notifications"""
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        query = Notification.query.filter_by(user_id=current_user_id)

        if unread_only:
            query = query.filter(Notification.read_at.is_(None))

        notifications = query.order_by(Notification.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': notifications.page,
            'unread_count': query.filter(Notification.read_at.is_(None)).count()
        }), 200

    except Exception as e:
        logger.error(f"Get notifications error: {str(e)}")
        return jsonify({'error': 'Failed to get notifications'}), 500

@app.route('/api/notifications/<notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        current_user_id = get_jwt_identity()

        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()

        if not notification:
            return jsonify({'error': 'Notification not found'}), 404

        NotificationService.mark_as_read(notification_id)
        db.session.commit()

        return jsonify({'message': 'Notification marked as read'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Mark notification read error: {str(e)}")
        return jsonify({'error': 'Failed to mark notification as read'}), 500

@app.route('/api/notifications/settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """Get user's notification settings"""
    try:
        current_user_id = get_jwt_identity()

        settings = UserNotificationSettings.query.filter_by(
            user_id=current_user_id
        ).first()

        if not settings:
            settings = NotificationService.create_default_settings(current_user_id)
            db.session.commit()

        return jsonify({'settings': settings.to_dict()}), 200

    except Exception as e:
        logger.error(f"Get notification settings error: {str(e)}")
        return jsonify({'error': 'Failed to get notification settings'}), 500

@app.route('/api/notifications/settings', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """Update user's notification settings"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        settings = NotificationService.update_settings(current_user_id, data)
        db.session.commit()

        return jsonify({
            'message': 'Notification settings updated successfully',
            'settings': settings.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Update notification settings error: {str(e)}")
        return jsonify({'error': 'Failed to update notification settings'}), 500

@app.route('/api/notifications/internal', methods=['POST'])
def receive_internal_notification():
    """Receive notifications from other services"""
    try:
        data = request.get_json()

        NotificationService.handle_internal_notification(
            notification_type=data['type'],
            user_id=data['user_id'],
            data=data['data']
        )

        db.session.commit()
        return jsonify({'message': 'Internal notification processed'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Internal notification error: {str(e)}")
        return jsonify({'error': 'Failed to process internal notification'}), 500