from django.test import TestCase

from catalog.models import Author, Book, BookInstance, Genre
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.utils import timezone



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

        
