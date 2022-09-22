from itertools import permutations
from pyexpat import model
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid # Требуется для уникальных экземпляров книг
from datetime import date

# Create your models here.
class Genre(models.Model):
    """Модель указывает на жанры книг"""
    name = models.CharField(max_length=200, 
                            help_text='Введите жанр книги')
    
    def __str__(self) -> str:
        """Текст для презентации объекта модели"""
        return self.name

    
class Book(models.Model):
    """Модель книги"""
    title = models.CharField(max_length=200)
    # книга может иметь одного автора, используем внешний ключ
    # модель автора еще не определена, поэтому выделена как текст
    author = models.ForeignKey('Author', 
                                on_delete=models.SET_NULL,
                                null=True)
    summary = models.TextField(max_length=1000,
                                help_text='Введите краткое описание книги')
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 символов <a href="https://www.isbn-international.org/content/what-isbn">ISBN номер</a>')
    # тип связи многие-ко-многим, так как одна книга может относиться к нескольким жанрам
    # модель жанров уже анонсирована, поэтому она выделена как объект
    genre = models.ManyToManyField(Genre, help_text='Выберите жанр книги')

    def __str__(self) -> str:
        """Текст для презентации модели"""
        return self.title    
        # return str((self.title, 
        #         '{0} {1}'.format(self.author.first_name, self.author.last_name),
        #         self.isbn,
        #         self.display_genre()))       
    
    def get_absolute_url(self):
        """Возвращает аюсолютный url на объект книги"""
        return reverse('book-detail', args=[str(self.id)])
    
    def display_genre(self):
        """Получаем текстовое название жанра для панели администратора"""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
    display_genre.short_description = 'Genre'

    class Meta:
        permissions = [('can_create_book', 'Can create/update/delete book')]


    # def get_author_name(self):
    #     """Достаем имя автора книги"""
    #     return '{0} {1}'.format(self.author.first_name, self.author.last_name)
        

class BookInstance(models.Model):
    """Модель копий каждой книги с идентификатором"""
    id = models.UUIDField(primary_key=True,
                        default=uuid.uuid4,
                        help_text='Уникальный номер для данного экземпляра по всей библиотеке')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'На обслуживании'),
        ('o', 'На руках'),
        ('a', 'Доступна'),
        ('r', 'Зарезервирована')
    )

    status = models.CharField(max_length=1,
                            choices=LOAN_STATUS,
                            blank=True,
                            default='m',
                            help_text='Доступность книги')
    
    class Meta:
        ordering = ['due_back']
        # разрешение на какое-либо действие 
        permissions = [('can_mark_returned', 'Set book as returned')]
    
    def __str__(self) -> str:
        """Текст для презентации модели"""
        return '{0} ({1})'.format(self.id, self.book.title)

    def get_author_name(self):
        """Достаем имя автора книги"""
        return self.book.author

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """Модель автора книги"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    def get_absolute_url(self):
        """Возвращает аюсолютный url на объект автора"""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self) -> str:
        """Текст для презентации модели"""
        return '{0}, {1}'.format(self.last_name, self.first_name)

    class Meta:
        permissions = [('can_create_author', 'Can create/update/delte author')]