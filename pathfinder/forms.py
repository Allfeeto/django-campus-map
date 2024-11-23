from django import forms
from .models import Node

class RouteForm(forms.Form):
    start = forms.ModelChoiceField(
        queryset=Node.objects.all(),
        label="Начальная точка",
        empty_label="Выберите начальную точку"
    )
    end = forms.ModelChoiceField(
        queryset=Node.objects.all(),
        label="Конечная точка",
        empty_label="Выберите конечную точку"
    )
