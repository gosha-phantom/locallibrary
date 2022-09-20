from django.shortcuts import render
from django.views import generic
from .models import Book, Author, Genre, BookInstance

# Create your views here.
def index(request):
    """Функция отображения  домашней страницы сайта"""
    # генерируем количества некоторых объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # количество доступных книг
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # количество авторов (метод all применен по умолчанию)
    num_authors = Author.objects.count()

    # количество жанров и книг по жанрам
    num_genre = Genre.objects.count()
    num_genre_books = Book.objects.filter(genre__name__contains='фэнтези').count()

    # отрисовка html-шаблона index.html с данными внутри
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'num_genre_books': num_genre_books
    }
    return render(request, 'index.html', context)


class BookListView(generic.ListView):
    model = Book
    # определение нового имени шаблона для вывода информации
    template_name = 'books.html'
    
    # context_object_name = 'books'
    
    # # переопределение методов в классах отображения
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='Ведьма')[:5]
    
    # # переопределение контекста (добавление новой переменной)
    # def get_context_data(self, **kwargs):
    #     # в первую очередь получаем контекст
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # добавляем новую переменную в контекст
    #     context['new_data'] = 'Добавленая в контекст информация'
    #     return context

class BookDetailView(generic.DetailView):
    model = Book
    # определение нового имени шаблона для вывода информации
    template_name = 'book.html'
    context_object_name = 'book'