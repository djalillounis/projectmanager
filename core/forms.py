from django import forms
from .models import Project, Item, Contact


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter project description'}),
        }


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_type', 'short_description', 'due_date', 'status', 'priority', 'owner', 'next_step_owner', 'next_step']
        widgets = {
            'next_step': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the next step'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'role', 'contact_type']
