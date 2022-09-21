from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as ul
import datetime

from django.forms import ModelForm
from .models import BookInstance

# реализация формы через свой собственнный класс (гибкий подход)
class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text='Введите дату не ранее сегодня и не позднее 4-х недель от сегодня (по умолчанию 3).', input_formats=['%Y-%m-%d'])

    def clean_renewal_date(self):
        """Валидация введенной даты"""
        data = self.cleaned_data['renewal_date']

        # проверка того, что дата не выходит за нижнюю границу
        if data < datetime.date.today():
            raise ValidationError(ul('Неверная дата - она находится в прошлом.'))
        
        # проверка того, что дата не выходит за верхнюю границу
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(ul('Невернаяя дата - она находится позже допустимых 4-ех недель.'))

        # возвращаем "очищенные" данные
        return data

# реализация через встроенный класс django.forms.ModelForm
# class RenewBookModelform(ModelForm):

#     # валидация
#     def clean_due_back(self):
#         data = self.cleaned_data['renewal_date']
#         # проверка того, что дата не выходит за нижнюю границу
#         if data < datetime.date.today():
#             raise ValidationError(ul('Неверная дата - она находится в прошлом.'))
#         # проверка того, что дата не выходит за верхнюю границу
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(ul('Невернаяя дата - она находится позже допустимых 4-ех недель.'))
#         # возвращаем "очищенные" данные
#         return data

#     class Meta:
#         model = BookInstance
#         fields = ['due_back']
#         labels = {'due_back': ul('Renewal date')}
#         help_texts = {'due_back': 'Введите дату не ранее сегодня и не позднее 4-х недель от сегодня (по умолчанию 3).'}
