from .models import Comment
from django import forms


class CommentCreationForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'title',
            'text',
        ]
