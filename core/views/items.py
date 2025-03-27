from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timezone import now
import json
import os
from django.conf import settings

from core.models import Item, Project
from core.forms import ItemForm


@login_required
def item_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project
            item.save()
            messages.success(request, "Item created successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ItemForm(initial={'item_type': request.GET.get('item_type')})
    return render(request, 'item_create.html', {'form': form, 'project': project})


@login_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    original_data = {
        "item_type": item.item_type,
        "short_description": item.short_description,
        "due_date": str(item.due_date),
        "status": item.status,
        "priority": item.priority,
        "owner": item.owner,
        "next_step_owner": item.next_step_owner,
    }

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        comment = request.POST.get("update_comment", "").strip()

        if not comment:
            messages.error(request, "A comment is required to update this item.")
            return render(request, 'item_edit.html', {'form': form, 'item': item})

        if form.is_valid():
            item = form.save(commit=False)
            update_file = request.FILES.get("update_file")
            change_notes = []

            # Compare changes
            for field, old_value in original_data.items():
                new_value = str(getattr(item, field))
                if new_value != old_value:
                    label = field.replace('_', ' ').capitalize()
                    change_notes.append(f"{label} changed from '{old_value}' to '{new_value}'")

            full_comment = "\n".join(change_notes)
            full_comment = f"{full_comment}\n\nUser comment: {comment}" if full_comment else comment

            update_entry = {
                "timestamp": now().isoformat(),
                "comment": full_comment,
            }

            if update_file:
                upload_dir = os.path.join(settings.MEDIA_ROOT, "updates")
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, update_file.name)

                with open(file_path, 'wb+') as destination:
                    for chunk in update_file.chunks():
                        destination.write(chunk)

                update_entry["file"] = f"/media/updates/{update_file.name}"

            if not item.updates:
                item.updates = []
            item.updates.append(update_entry)

            item.save()
            messages.success(request, "Item updated successfully!")
            return redirect('project_detail', project_id=item.project.id)

    else:
        form = ItemForm(instance=item)

    return render(request, 'item_edit.html', {'form': form, 'item': item})


@require_POST
@login_required
def update_next_step(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    data = json.loads(request.body)
    item.next_step_owner = data.get('next_step_owner')
    item.save()
    return JsonResponse({'success': True})
