from atexit import register
from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

# Register your models here.
admin.site.register(Genre)

# определяем класс для отображения дополнений по книгам
class BookInline(admin.TabularInline):
    model = Book
    fields = ('title', 'isbn', 'genre')
    extra = 0

# определяем класс автора
class AuthorAdmin(admin.ModelAdmin):
    # отображение данных при отображении всех данных
    list_display = ('last_name',
                    'first_name',
                    'date_of_birth',
                    'date_of_death')
    # отображение данных при добавлении новой записи 
    fields = ['first_name', 'last_name',
                ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]
# регистрируем класс автора
admin.site.register(Author, AuthorAdmin)


# определяем класс копий книг
# регистрируем класс копий книг
@admin.register(BookInstance)
# создаем новые представления в админке
class BookInstanceAdmin(admin.ModelAdmin):
    # отображение данных при отображении всех данных
    list_display = ('book',
                    'get_author_name',
                    'status',
                    'borrower',
                    'due_back',
                    'id')
    list_filter = ('status', 'due_back')
    # отображение данных при добавлении новой записи
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        })
    )

# определяем класс для отображения дополнений по копиям книг
class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    fields = ('id', 'status', 'due_back')
    extra = 0

# определяем класс книг
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'author',
                    'display_genre')
    inlines = [BookInstanceInline]


    

