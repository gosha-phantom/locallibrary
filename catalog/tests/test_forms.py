from django.test import TestCase

import datetime
from django.utils import timezone
from catalog.forms import RenewBookForm

# Create your tests here.
class RenewBookFormTest(TestCase):

    def setUp(self) -> None:
        self.form = RenewBookForm()
        
    def test_renew_form_date_field_label(self):
        self.assertTrue(self.form.fields['renewal_date'].label==None or self.form.fields['renewal_date']=='renewal_date')

    def test_renew_form_date_field_help_text(self):
        self.assertTrue(self.form.fields['renewal_date'].help_text, 'Введите дату не ранее сегодня и не позднее 4-х недель от сегодня (по умолчанию 3).')

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=5)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.now() + datetime.timedelta(weeks=3)
        # print('Timezone: ', timezone.now())
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())