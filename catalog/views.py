from django.shortcuts import render
from django.views import generic
from .models import Book, Author, Genre, BookInstance
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# импортиркуем модуль управления разрешениями из моделей для функций view
from django.contrib.auth.decorators import permission_required
# импортиркуем модуль управления разрешениями из моделей для классов view
from django.contrib.auth.mixins import PermissionRequiredMixin


# Create your views here.
# @permission_required('can_mark_returned')
def index(request):
    """Функция отображения  домашней страницы сайта"""
    # генерируем количества некоторых объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # количество доступных книг
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # количество авторов (метод all применен по умолчанию)
    num_authors = Author.objects.count()

    # количество визитов на сайт
    # если значение num_visits отсутствует, тогда по умолчанию устанавливается 0
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

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
        'num_genre_books': num_genre_books,
        'num_visits': num_visits
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


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
        Общее представление на основе класса, в котором перечислены книги,
        предоставленные текущему пользователю.
    """
    model = BookInstance
    template_name = 'bi_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

# class LoanedBooksByUserForLybListView(LoginRequiredMixin, generic.ListView):
#     """
#         Общее представление на основе класса, в котором перечислены книги,
#         предоставленные текущему пользователю.
#     """
#     model = BookInstance
#     template_name = 'bi_list_borrowed_user_forlyb.html'
#     paginate_by = 10

#     def get_queryset(self):
#         return BookInstance.objects.filter(status__exact='o').order_by('due_back')



class LoanedBooksByUserForLybrarian(PermissionRequiredMixin, generic.ListView):
    permission_required = 'can_mark_returned'
    """
        Общее представление на основе класса, в котором перечислены книги,
        предоставленные пользователям.
    """
    model = BookInstance
    template_name = 'bi_list_borrowed_user_forlyb.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')