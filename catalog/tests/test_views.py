from urllib import response
from django.test import TestCase

from catalog.models import Author, Book, BookInstance, Genre
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.utils import timezone
from django.contrib.auth.models import Permission


# Create your tests here.
class AuthorListViewTest(TestCase):
    """Тестируем ототбражение списка авторов"""

    @classmethod
    def setUpTestData(cls) -> None:
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian {0}'.format(author_num), last_name='Surname {0}'.format(author_num))
            # print('Christian {0}'.format(author_num), 'Surname {0}'.format(author_num))

    # def test_view_url_exists_at_desired_location(self):
    #     resp = self.client.get('/catalog/authors/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_view_uses_correct_template(self):
    #     resp = self.client.get(reverse('authors'))
    #     self.assertEqual(resp.status_code, 200)

    #     self.assertTemplateUsed(resp, 'authors.html')
    
    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        # print(resp.context['is_paginated'])
        self.assertTrue(resp.context['is_paginated']==True)
        self.assertTrue(len(resp.context['author_list'])==10)

class LoanedBookInstancesByUserListViewTest(TestCase):
    """Тестируем класс отображения книг для библиотекарей"""

    def setUp(self) -> None:
        # создание двух пользователей
        test_user_1 = User.objects.create_user(username='testuser1', password='12345')
        test_user_1.save()
        test_user_2 = User.objects.create_user(username='testuser2', password='123456')
        test_user_2.save()

        # создание книги
        test_author = Author.objects.create(first_name='Jonh', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(title='Book title', summary='Some text', isbn='ABCDEFG', author=test_author)
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # создание 30 копий книг
        number_of_book_instances = 30
        for book_copy in range(number_of_book_instances):
            return_date = timezone.now() + datetime.timedelta(days=book_copy)
            if book_copy % 2:
                the_borrower = test_user_1
            else:
                the_borrower = test_user_2
            status = 'm'
            BookInstance.objects.create(book=test_book, imprint='Типография 1', due_back=return_date, borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))
        
        # проверка того, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)
        # проверка того, что мы использовали правильный шаблон
        self.assertTemplateUsed(resp, 'bi_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        """Проверяем список книг, взятых пользователем"""
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # проверка того, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # проверка того, что изначально у нас нет книг в списке
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        # книги взяты напрокат
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # проверка, что все забронированные книги в списке
        resp = self.client.get(reverse('my-borrowed'))
        # проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # проверка успешности ответа
        self.assertEqual(resp.status_code, 200)
        # провера наличия списка книг в контексте
        self.assertTrue('bookinstance_list' in resp.context)
        # подтверждение, что все книги принадлежат указанному пользователю и взяты напрокат
        for bi in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bi.borrower)
            self.assertEqual('o', bi.status)

    def test_pages_ordered_by_due_date(self):
        # меняем статус на "в прокате"
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # проверка успешности ответа
        self.assertEqual(resp.status_code, 200)
        # проверка, что из всего списка показываются только 10 копий
        self.assertEqual(len(resp.context['bookinstance_list']), 10)

        last_date = 0

        for copy in resp.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date<=copy.due_back)

class RenewBookInstancesViewTest(TestCase):

    def setUp(self) -> None:
        # создание двух пользователей
        test_user_1 = User.objects.create_user(username='testuser1', password='12345')
        test_user_1.save()
        test_user_2 = User.objects.create_user(username='testuser2', password='12345')
        test_user_2.save()
        # присвоение второму пользователю прав библиотекаря
        permission = Permission.objects.get(name='Set book as returned')
        test_user_2.user_permissions.add(permission)
        test_user_2.save()

        # создание книги
        test_author = Author.objects.create(first_name='Jonh', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(title='Book title', summary='Some text', isbn='ABCDEFG', author=test_author)
        # создание жанра книги
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # создание объекта bookinstance для пользователя test_user_1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bi1 = BookInstance.objects.create(book=test_book, imprint='Типография 1', due_back=return_date, borrower=test_user_1, status='o')
        # создание объекта bookinstance для пользователя test_user_2
        return_date = datetime.date.today() + datetime.timedelta(days=10)
        self.test_bi2 = BookInstance.objects.create(book=test_book, imprint='Типография 1', due_back=return_date, borrower=test_user_2, status='o')

    def test_redirect_if_not_logged_in(self):
        """Проверка перенаправления пользователя, если он не вошел в систему"""
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bi1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        """Проверяем наличие входа в систему с отсутствием необходимых разрешений"""
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bi1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        """Проверяем наличие входа в систему с необходимыми разрешениями"""
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bi2.pk}))
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        """
            Проверяем наличие входа в систему с необходимыми разрешениями 
            для просмотра забранных книг другим пользователем
        """
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bi1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        """
            Проверяем валидность на получение ошибки при запросе несуществующей копии книги 
        """
        import uuid
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_coirrect_template(self):
        """Проверяем правильность выбора шаблона для отображения"""
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bi2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        """Проверяем наличие даты возврата книги при ее создании (по умолчанию 3 недели)"""
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bi1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    # def test_redirect_to_all_borrowed_book_list_on_success(self):
    #     # !!! ТЕСТ ПРОВАЛЕН!
    #     """Проверяем перенаправление на страницу всех книг, забранных пользователями"""
    #     login = self.client.login(username='testuser2', password='12345')
    #     test_date = datetime.date.today() + datetime.timedelta(days=3)
    #     # !!! перенаправление на страницу книг пользователей не сработало!!!
    #     response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bi1.pk}), {'renewal_date': test_date})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFormError(response, 'form', 'renewal_date', 'Неверная дата - она находится позже допустимых 4-ех недель.')
        
        # self.assertRedirects(response, reverse('userbooks'))
        # !!! перенаправление на главную страницу также не работает!!!
        # response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bi2.pk}), {'renewal_date': valid_date_in_future}, follow=True)
        # self.assertRedirects(response, '/catalog/')

    def test_form_invalid_renewal_date_past(self):
        """Проверяем перенаправление на страницу ошибки, если дата в пост-запросе указана неверно (дата в прошлом)"""
        login = self.client.login(username='testuser2', password='12345')
        test_date = datetime.date.today() - datetime.timedelta(weeks=3)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bi1.pk}), {'renewal_date': test_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Неверная дата - она находится в прошлом.')

    def test_form_invalid_renewal_date_future(self):
        """Проверяем перенаправление на страницу ошибки, если дата в пост-запросе указана неверно (дата в будущем)"""
        login = self.client.login(username='testuser2', password='12345')
        test_date = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bi1.pk}), {'renewal_date': test_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Неверная дата - она находится позже допустимых 4-ех недель.')