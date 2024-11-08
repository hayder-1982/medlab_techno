from django import forms

from .models import CommentModel,ResultModel,CBCModel


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['text']

class ResultForm(forms.ModelForm):
    class Meta:
        model = ResultModel
        fields = ['test']


class CBCForm(forms.ModelForm):
    class Meta:
        model = CBCModel
        fields = '__all__' 
