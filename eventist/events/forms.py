from django import forms

class EventSearchForm(forms.Form):
    search_term = forms.CharField(max_length=255, required=True, label='Search')
