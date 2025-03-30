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
        fields = [
            'item_type', 'short_description', 'due_date', 'status',
            'priority', 'owner', 'next_step_owner', 'next_step'
        ]
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'owner': forms.TextInput(attrs={'class': 'form-control'}),
            'next_step_owner': forms.TextInput(attrs={'class': 'form-control'}),
            'next_step': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe the next step',
                'class': 'form-control'
            }),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'role', 'contact_type']
