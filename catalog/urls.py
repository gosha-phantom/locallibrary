from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^books/$', views.BookListView.as_view(), name='books'),
    re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
    re_path(r'^mybooks/$', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    re_path(r'^userbooks/$', views.LoanedBooksByUserForLibrarian.as_view(), name='userbooks'),
    # страница для обновления данных по отданным книгам
    re_path(r'^book/(?P<pk>[-\w]+)/$', views.renew_book_librariran, name='renew-book-librariran')
]