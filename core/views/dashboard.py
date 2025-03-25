from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Item, Project


def get_open_items_summary():
    """Returns open item count by type and priority."""
    summary = {
        'task': {'High': 0, 'Medium': 0, 'Low': 0},
        'sub_project': {'High': 0, 'Medium': 0, 'Low': 0},
        'activity': {'High': 0, 'Medium': 0, 'Low': 0},
    }

    open_items = Item.objects.exclude(status__in=['completed', 'cancelled'])

    for item in open_items:
        item_type = item.item_type
        priority = item.priority
        if item_type in summary and priority in summary[item_type]:
            summary[item_type][priority] += 1

    return summary


@login_required
def dashboard(request):
    summary = get_open_items_summary()
    projects = Project.objects.all()
    return render(request, 'dashboard.html', {
        'summary': summary,
        'projects': projects
    })
