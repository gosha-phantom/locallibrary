# импортируем исключении ошибки http404
from django.http import Http404

# функция проверки объекта либо возврата ошибки
def get_object_or_404(Obj, pk):
    """Проверяем, существует ли объект на входе в функцию в приложении"""
    try:
        return Obj.objects.get(pk=pk)
    except:
        return Http404('Объект не существует')