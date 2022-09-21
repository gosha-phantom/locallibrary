from django.shortcuts import render
from django.views import generic
from .models import Book, Author, Genre, BookInstance
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# импортиркуем модуль управления разрешениями из моделей для функций view
from django.contrib.auth.decorators import permission_required
# импортируем модуль управления разрешениями из моделей для классов view
from django.contrib.auth.mixins import PermissionRequiredMixin
# импортируем формы
from .forms import RenewBookForm
# импортируем функции
# from .functions import get_object_or_404
from django.shortcuts import get_object_or_404
# импоритуем функцию перенаправления на другие url-ы
from django.urls import reverse
from django.http import HttpResponseRedirect
# импортируем модуль работы с датами и временем
import datetime


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


class LoanedBooksByUserForLibrarian(PermissionRequiredMixin, generic.ListView):
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

@permission_required('catalog.can_mark_returned')
def renew_book_librariran(request, pk):
    """Функция для изменения данных забранных книг"""
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # если данный запрос типа post
    if request.method == 'POST':
        # создаем экземпляр формы и заполняем её данными
        form = RenewBookForm(request.POST)

        # проверка валидности данных формы
        if form.is_valid():
            # обработка данных из form.cleaned_data
            # здесь мы просто присваиваем их полю due_back
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            # переход по адресу 'userbooks'
            return HttpResponseRedirect(reverse('userbooks'))
        
    # если это get-запрос
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    
    return render(request, 'book_renew_librarian.html', {'form': form, 'bookinst': book_inst})


