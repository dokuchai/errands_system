from django.db import models


class ChangeloggableMixin(models.Model):
    """Значения полей сразу после инициализации объекта"""
    _original_values = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ChangeloggableMixin, self).__init__(*args, **kwargs)

        self._original_values = {
            field.name: getattr(self, field.name)
            for field in self._meta.fields if field.name not in ['added', 'changed'] and hasattr(self, field.name)
        }
        # self._state.fields_cache.update({
        #     field.name: getattr(self, field.name).all()
        #     for field in self._meta.many_to_many if hasattr(self, field.name)
        # })
        # self.__dict__.update({
        #     field.name: getattr(self, field.name).all()
        #     for field in self._meta.many_to_many if hasattr(self, field.name)
        # })

    def get_changed_fields(self):
        """
        Получаем измененные данные
        """
        self._original_values.update({
            field.name: getattr(self, field.name)
            for field in self._meta.many_to_many if hasattr(self, field.name)
        })
        result = {}
        for name, value in self._original_values.items():
            if value != getattr(self, name):
                temp = {}
                temp[name] = getattr(self, name)
                result.update(temp)
            if hasattr(value, 'all') and list(value.all()) != list(getattr(self, name).all()):
                temp = {}
                so_executors = [so_executor for so_executor in getattr(self, name).all()]
                temp[name] = so_executors
                result.update(temp)
        # result.update({name: getattr(self, name) for name, value in self._original_values.items() if
        #                value != getattr(self, name)})
        # result.update(
        #     {'so_executors': [so_executor for so_executor in self._original_values.get('so_executors').all() if
        #                       'so_executors' in self._original_values.keys()]})
        return result
