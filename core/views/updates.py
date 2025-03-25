from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from core.models import Item
from django.core.files.storage import default_storage


@require_POST
@login_required
def delete_update(request, item_id, timestamp):
    item = get_object_or_404(Item, id=item_id)
    updates = item.updates or []
    filtered_updates = [u for u in updates if u.get("timestamp") != timestamp]

    if len(filtered_updates) < len(updates):
        item.updates = filtered_updates
        item.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Update not found'})


@require_POST
@login_required
def delete_item_file(request, item_id, timestamp):
    item = get_object_or_404(Item, id=item_id)
    updates = item.updates or []
    updated = False

    for update in updates:
        if update.get("timestamp") == timestamp and "file" in update:
            file_path = update["file"]
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            del update["file"]
            updated = True

    if updated:
        item.updates = updates
        item.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'File not found'})
