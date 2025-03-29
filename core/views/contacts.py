from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render

from core.models import Project, Contact
from core.forms import ContactForm


@require_POST
@login_required
def add_contact(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    form = ContactForm(request.POST)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.project = project
        contact.save()

        # ✅ This is required to return HTML for the new contact
        contact_html = render_to_string("project/partials/contact_card.html", {"contact": contact})
        return JsonResponse({'success': True, 'contact_html': contact_html})
    
    return JsonResponse({'success': False, 'errors': form.errors})

@require_POST
@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    contact.delete()
    return JsonResponse({'success': True})


@require_POST
@login_required
def update_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    form = ContactForm(request.POST, instance=contact)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})
