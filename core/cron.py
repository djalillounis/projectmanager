from datetime import timedelta, date
from django.core.mail import send_mail
from .models import Item

def send_due_soon_notifications():
    notify_date = date.today() + timedelta(days=5)
    items = Item.objects.filter(due_date=notify_date, status__in=['new', 'in_progress', 'on_hold'])
    for item in items:
        subject = f"Upcoming Due Date for {item.short_description}"
        message = (
            f"Project: {item.project.name}\n"
            f"Item: {item.short_description}\n"
            f"Due: {item.due_date}\n"
            f"Priority: {item.priority}"
        )
        send_mail(subject, message, 'your-email@example.com', [item.owner])
