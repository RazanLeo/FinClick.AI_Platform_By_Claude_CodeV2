"""
Notification Agent
وكيل إدارة الإشعارات

This agent manages all notifications, alerts, and communications within the
FinClick.AI platform, ensuring timely delivery of important information.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ALERT = "alert"
    REMINDER = "reminder"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    SLACK = "slack"
    TEAMS = "teams"


@dataclass
class Notification:
    """Notification message"""
    notification_id: str
    type: NotificationType
    priority: NotificationPriority
    title_ar: str
    title_en: str
    message_ar: str
    message_en: str
    recipient: str
    channels: List[NotificationChannel]
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


class NotificationAgent(FinancialAgent):
    """
    Specialized agent for notifications and alerts management
    وكيل متخصص في إدارة الإشعارات والتنبيهات
    """

    def __init__(self, agent_id: str = "notification_agent",
                 agent_name_ar: str = "وكيل إدارة الإشعارات",
                 agent_name_en: str = "Notification Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'NOTIFICATION', 'notification')
        )

        self.notification_queue = []
        self.notification_templates = self._initialize_notification_templates()
        self.channel_configs = self._initialize_channel_configs()

    def _initialize_capabilities(self) -> None:
        """Initialize notification capabilities"""
        self.capabilities = {
            "notification_types": {
                "workflow_notifications": True,
                "analysis_alerts": True,
                "system_notifications": True,
                "compliance_alerts": True,
                "performance_alerts": True,
                "error_notifications": True
            },
            "channels": {
                "email": True,
                "sms": False,  # Requires SMS service setup
                "push_notifications": True,
                "in_app": True,
                "slack": False,  # Requires Slack integration
                "microsoft_teams": False  # Requires Teams integration
            },
            "features": {
                "scheduled_notifications": True,
                "notification_templates": True,
                "priority_routing": True,
                "delivery_tracking": True,
                "escalation_management": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_notification_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize notification templates"""
        return {
            "workflow_started": {
                "title_ar": "بدء سير العمل",
                "title_en": "Workflow Started",
                "message_ar": "تم بدء سير العمل {workflow_name} بنجاح",
                "message_en": "Workflow {workflow_name} has been started successfully",
                "priority": NotificationPriority.MEDIUM,
                "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
            },
            "workflow_completed": {
                "title_ar": "اكتمال سير العمل",
                "title_en": "Workflow Completed",
                "message_ar": "تم إكمال سير العمل {workflow_name} بنجاح في {execution_time} دقيقة",
                "message_en": "Workflow {workflow_name} completed successfully in {execution_time} minutes",
                "priority": NotificationPriority.MEDIUM,
                "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
            },
            "workflow_failed": {
                "title_ar": "فشل سير العمل",
                "title_en": "Workflow Failed",
                "message_ar": "فشل في تنفيذ سير العمل {workflow_name}. السبب: {error_message}",
                "message_en": "Workflow {workflow_name} failed. Reason: {error_message}",
                "priority": NotificationPriority.HIGH,
                "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.PUSH]
            },
            "compliance_violation": {
                "title_ar": "مخالفة امتثال",
                "title_en": "Compliance Violation",
                "message_ar": "تم اكتشاف مخالفة امتثال: {violation_description}",
                "message_en": "Compliance violation detected: {violation_description}",
                "priority": NotificationPriority.URGENT,
                "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.PUSH]
            },
            "risk_alert": {
                "title_ar": "تنبيه مخاطر",
                "title_en": "Risk Alert",
                "message_ar": "تم تحديد مخاطر عالية: {risk_description}",
                "message_en": "High risk identified: {risk_description}",
                "priority": NotificationPriority.HIGH,
                "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
            },
            "analysis_ready": {
                "title_ar": "التحليل جاهز",
                "title_en": "Analysis Ready",
                "message_ar": "تم إكمال التحليل المالي للشركة {company_name}",
                "message_en": "Financial analysis completed for {company_name}",
                "priority": NotificationPriority.MEDIUM,
                "channels": [NotificationChannel.IN_APP]
            },
            "system_maintenance": {
                "title_ar": "صيانة النظام",
                "title_en": "System Maintenance",
                "message_ar": "صيانة مجدولة للنظام من {start_time} إلى {end_time}",
                "message_en": "Scheduled system maintenance from {start_time} to {end_time}",
                "priority": NotificationPriority.MEDIUM,
                "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
            }
        }

    def _initialize_channel_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize channel configurations"""
        return {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_tls": True,
                "rate_limit": 100,  # emails per hour
                "template_format": "html"
            },
            "sms": {
                "enabled": False,
                "provider": "twilio",
                "rate_limit": 50,  # SMS per hour
                "character_limit": 160
            },
            "push": {
                "enabled": True,
                "service": "firebase",
                "rate_limit": 1000,  # push notifications per hour
                "title_length_limit": 50
            },
            "in_app": {
                "enabled": True,
                "retention_days": 30,
                "max_notifications": 100
            }
        }

    async def send_notification(self, template_name: str, recipient: str,
                              variables: Dict[str, Any] = None,
                              channels: List[NotificationChannel] = None,
                              priority: NotificationPriority = None) -> Dict[str, Any]:
        """
        Send notification using specified template
        إرسال إشعار باستخدام القالب المحدد
        """
        try:
            # Get template
            template = self.notification_templates.get(template_name)
            if not template:
                return {"error": f"Template {template_name} not found"}

            # Prepare notification
            variables = variables or {}
            notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{recipient}"

            # Format messages
            title_ar = template["title_ar"].format(**variables)
            title_en = template["title_en"].format(**variables)
            message_ar = template["message_ar"].format(**variables)
            message_en = template["message_en"].format(**variables)

            # Create notification
            notification = Notification(
                notification_id=notification_id,
                type=self._determine_notification_type(template_name),
                priority=priority or template["priority"],
                title_ar=title_ar,
                title_en=title_en,
                message_ar=message_ar,
                message_en=message_en,
                recipient=recipient,
                channels=channels or template["channels"],
                created_at=datetime.now(),
                metadata=variables
            )

            # Send through channels
            delivery_results = {}
            for channel in notification.channels:
                result = await self._send_through_channel(notification, channel)
                delivery_results[channel.value] = result

            # Track notification
            await self._track_notification(notification, delivery_results)

            return {
                "notification_id": notification_id,
                "status": "sent",
                "delivery_results": delivery_results,
                "sent_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Notification sending failed: {str(e)}"}

    def _determine_notification_type(self, template_name: str) -> NotificationType:
        """Determine notification type from template name"""
        if "failed" in template_name or "error" in template_name:
            return NotificationType.ERROR
        elif "violation" in template_name or "alert" in template_name:
            return NotificationType.ALERT
        elif "completed" in template_name or "ready" in template_name:
            return NotificationType.SUCCESS
        elif "warning" in template_name:
            return NotificationType.WARNING
        else:
            return NotificationType.INFO

    async def _send_through_channel(self, notification: Notification,
                                  channel: NotificationChannel) -> Dict[str, Any]:
        """Send notification through specific channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(notification)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(notification)
            elif channel == NotificationChannel.PUSH:
                return await self._send_push_notification(notification)
            elif channel == NotificationChannel.IN_APP:
                return await self._send_in_app_notification(notification)
            else:
                return {"status": "not_implemented", "channel": channel.value}

        except Exception as e:
            return {"status": "failed", "error": str(e), "channel": channel.value}

    async def _send_email(self, notification: Notification) -> Dict[str, Any]:
        """Send email notification (mock implementation)"""
        # In real implementation, would use actual email service
        await asyncio.sleep(0.1)  # Simulate email sending delay

        return {
            "status": "sent",
            "channel": "email",
            "recipient": notification.recipient,
            "sent_at": datetime.now().isoformat(),
            "message_id": f"email_{notification.notification_id}"
        }

    async def _send_sms(self, notification: Notification) -> Dict[str, Any]:
        """Send SMS notification (mock implementation)"""
        if not self.channel_configs["sms"]["enabled"]:
            return {"status": "disabled", "channel": "sms"}

        # Truncate message for SMS
        message = notification.message_en[:160]

        await asyncio.sleep(0.05)  # Simulate SMS sending delay

        return {
            "status": "sent",
            "channel": "sms",
            "recipient": notification.recipient,
            "sent_at": datetime.now().isoformat(),
            "message_length": len(message)
        }

    async def _send_push_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send push notification (mock implementation)"""
        await asyncio.sleep(0.02)  # Simulate push notification delay

        return {
            "status": "sent",
            "channel": "push",
            "recipient": notification.recipient,
            "sent_at": datetime.now().isoformat(),
            "title": notification.title_en[:50]  # Truncate title
        }

    async def _send_in_app_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send in-app notification"""
        # Store in notification queue for in-app display
        self.notification_queue.append({
            "id": notification.notification_id,
            "type": notification.type.value,
            "priority": notification.priority.value,
            "title": notification.title_en,
            "message": notification.message_en,
            "created_at": notification.created_at.isoformat(),
            "read": False
        })

        # Keep only recent notifications
        max_notifications = self.channel_configs["in_app"]["max_notifications"]
        if len(self.notification_queue) > max_notifications:
            self.notification_queue = self.notification_queue[-max_notifications:]

        return {
            "status": "sent",
            "channel": "in_app",
            "recipient": notification.recipient,
            "queued_at": datetime.now().isoformat()
        }

    async def _track_notification(self, notification: Notification,
                                delivery_results: Dict[str, Any]) -> None:
        """Track notification delivery"""
        # In real implementation, would store in database
        pass

    async def get_user_notifications(self, user_id: str,
                                   limit: int = 50,
                                   unread_only: bool = False) -> Dict[str, Any]:
        """
        Get notifications for a specific user
        الحصول على الإشعارات لمستخدم محدد
        """
        try:
            # Filter notifications for user
            user_notifications = [
                notif for notif in self.notification_queue
                # In real implementation, would filter by user_id
            ]

            if unread_only:
                user_notifications = [
                    notif for notif in user_notifications
                    if not notif.get("read", False)
                ]

            # Sort by creation time (newest first)
            user_notifications.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )

            # Apply limit
            user_notifications = user_notifications[:limit]

            return {
                "notifications": user_notifications,
                "total_count": len(user_notifications),
                "unread_count": len([n for n in user_notifications if not n.get("read", False)])
            }

        except Exception as e:
            return {"error": f"Failed to get notifications: {str(e)}"}

    async def mark_notification_read(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """
        Mark notification as read
        تحديد الإشعار كمقروء
        """
        try:
            for notification in self.notification_queue:
                if notification["id"] == notification_id:
                    notification["read"] = True
                    notification["read_at"] = datetime.now().isoformat()
                    return {"status": "marked_read", "notification_id": notification_id}

            return {"error": f"Notification {notification_id} not found"}

        except Exception as e:
            return {"error": f"Failed to mark notification as read: {str(e)}"}

    async def schedule_notification(self, template_name: str, recipient: str,
                                  scheduled_time: datetime,
                                  variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Schedule notification for future delivery
        جدولة إشعار للتسليم المستقبلي
        """
        try:
            notification_id = f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{recipient}"

            # In real implementation, would store in database with scheduler
            scheduled_notification = {
                "notification_id": notification_id,
                "template_name": template_name,
                "recipient": recipient,
                "variables": variables or {},
                "scheduled_time": scheduled_time.isoformat(),
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }

            return {
                "notification_id": notification_id,
                "status": "scheduled",
                "scheduled_for": scheduled_time.isoformat()
            }

        except Exception as e:
            return {"error": f"Failed to schedule notification: {str(e)}"}

    async def send_bulk_notification(self, template_name: str,
                                   recipients: List[str],
                                   variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send notification to multiple recipients
        إرسال إشعار لعدة مستلمين
        """
        try:
            results = []
            successful = 0
            failed = 0

            for recipient in recipients:
                result = await self.send_notification(
                    template_name=template_name,
                    recipient=recipient,
                    variables=variables
                )

                results.append({
                    "recipient": recipient,
                    "status": "success" if "error" not in result else "failed",
                    "details": result
                })

                if "error" not in result:
                    successful += 1
                else:
                    failed += 1

            return {
                "total_recipients": len(recipients),
                "successful": successful,
                "failed": failed,
                "results": results,
                "sent_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Bulk notification failed: {str(e)}"}

    async def create_custom_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and send custom notification
        إنشاء وإرسال إشعار مخصص
        """
        try:
            notification_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create notification from custom data
            notification = Notification(
                notification_id=notification_id,
                type=NotificationType(notification_data.get("type", "info")),
                priority=NotificationPriority(notification_data.get("priority", "medium")),
                title_ar=notification_data.get("title_ar", ""),
                title_en=notification_data.get("title_en", ""),
                message_ar=notification_data.get("message_ar", ""),
                message_en=notification_data.get("message_en", ""),
                recipient=notification_data.get("recipient", ""),
                channels=[NotificationChannel(ch) for ch in notification_data.get("channels", ["in_app"])],
                created_at=datetime.now(),
                metadata=notification_data.get("metadata", {})
            )

            # Send through channels
            delivery_results = {}
            for channel in notification.channels:
                result = await self._send_through_channel(notification, channel)
                delivery_results[channel.value] = result

            return {
                "notification_id": notification_id,
                "status": "sent",
                "delivery_results": delivery_results
            }

        except Exception as e:
            return {"error": f"Custom notification failed: {str(e)}"}

    async def get_notification_statistics(self) -> Dict[str, Any]:
        """
        Get notification delivery statistics
        الحصول على إحصائيات تسليم الإشعارات
        """
        try:
            # Mock statistics - in real implementation, would query database
            return {
                "total_notifications": len(self.notification_queue),
                "notifications_today": len([
                    n for n in self.notification_queue
                    if datetime.fromisoformat(n["created_at"]).date() == datetime.now().date()
                ]),
                "by_type": {
                    "info": len([n for n in self.notification_queue if n["type"] == "info"]),
                    "warning": len([n for n in self.notification_queue if n["type"] == "warning"]),
                    "error": len([n for n in self.notification_queue if n["type"] == "error"]),
                    "success": len([n for n in self.notification_queue if n["type"] == "success"]),
                    "alert": len([n for n in self.notification_queue if n["type"] == "alert"])
                },
                "by_priority": {
                    "low": len([n for n in self.notification_queue if n["priority"] == "low"]),
                    "medium": len([n for n in self.notification_queue if n["priority"] == "medium"]),
                    "high": len([n for n in self.notification_queue if n["priority"] == "high"]),
                    "urgent": len([n for n in self.notification_queue if n["priority"] == "urgent"])
                },
                "unread_count": len([n for n in self.notification_queue if not n.get("read", False)]),
                "channel_usage": {
                    "in_app": len(self.notification_queue),
                    "email": 0,  # Would be tracked from delivery results
                    "push": 0,
                    "sms": 0
                }
            }

        except Exception as e:
            return {"error": f"Failed to get statistics: {str(e)}"}

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process notification tasks"""
        try:
            task_type = task.task_data.get("type", "send_notification")

            if task_type == "send_notification":
                template_name = task.task_data.get("template_name", "")
                recipient = task.task_data.get("recipient", "")
                variables = task.task_data.get("variables", {})
                channels = task.task_data.get("channels")
                priority = task.task_data.get("priority")

                if channels:
                    channels = [NotificationChannel(ch) for ch in channels]
                if priority:
                    priority = NotificationPriority(priority)

                return await self.send_notification(template_name, recipient, variables, channels, priority)

            elif task_type == "get_notifications":
                user_id = task.task_data.get("user_id", "")
                limit = task.task_data.get("limit", 50)
                unread_only = task.task_data.get("unread_only", False)
                return await self.get_user_notifications(user_id, limit, unread_only)

            elif task_type == "mark_read":
                notification_id = task.task_data.get("notification_id", "")
                user_id = task.task_data.get("user_id", "")
                return await self.mark_notification_read(notification_id, user_id)

            elif task_type == "bulk_notification":
                template_name = task.task_data.get("template_name", "")
                recipients = task.task_data.get("recipients", [])
                variables = task.task_data.get("variables", {})
                return await self.send_bulk_notification(template_name, recipients, variables)

            elif task_type == "custom_notification":
                notification_data = task.task_data.get("notification_data", {})
                return await self.create_custom_notification(notification_data)

            elif task_type == "get_statistics":
                return await self.get_notification_statistics()

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}