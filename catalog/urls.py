from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^books/$', views.BookListView.as_view(), name='books'),
    re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
    re_path(r'^mybooks/$', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    re_path(r'^userbooks/$', views.LoanedBooksByUserForLibrarian.as_view(), name='userbooks'),
    # страница для обновления данных по отданным книгам
    re_path(r'^book/(?P<pk>[-\w]+)/$', views.renew_book_librariran, name='renew-book-librarian'),
    # страницы по созданию/изменению/удалению авторов
    re_path(r'^author/create/$', views.AuthorCreateView.as_view(), name='author_create'),
    re_path(r'^author/(?P<pk>\d+)/update/$', views.AuthorUpdateView.as_view(), name='author_update'),
    re_path(r'^author/(?P<pk>\d+)/delete/$', views.AuthorDeleteView.as_view(), name='author_delete'),
    re_path(r'^authors/$', views.AuthorListView.as_view(), name='authors'),
    # страница просмотра детализации по автору
    re_path(r'^authors/(?P<pk>\d+)$', views.AuthorDetailView.as_view(), name='author-detail'),
    # страницы по созданию/изменению/удалению книг
    re_path(r'^books/create/$', views.BookCreateView.as_view(), name='book_create'),
    re_path(r'^book/(?P<pk>\d+)/update/$', views.BookUpdateView.as_view(), name='book_update'),
    re_path(r'^book/(?P<pk>\d+)/delete/$', views.BookDeleteView.as_view(), name='book_delete'),
    
]