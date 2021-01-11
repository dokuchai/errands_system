from django.db import models
from django.db.models.options import make_immutable_fields_list


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
        # self._original_values.update({
        #     field.name: getattr(self, field.name)
        #     for field in self._meta.many_to_many if hasattr(self, field.name)
        # })
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
        result = {}
        print(self.__dict__.keys())
        for name, value in self._original_values.items():
            # print(name, value, value != getattr(self, name))
            if value != getattr(self, name):
                print(value, getattr(self, name))
                temp = {}
                temp[name] = getattr(self, name)
                result.update(temp)
            # if hasattr(value, 'all') and value.all() != getattr(self, name).all():
            # print(dir(self._meta.local_many_to_many[0]))
            # print(value.set.__self__.values('email'))
            # print(value.all())
            # print(getattr(self, name).all())
            # print([_ for _ in value.all()] != [_ for _ in getattr(self, name).all()])
            # print([obj for obj in value.all()])
            # print(value.all(), getattr(self, 'so_executors').all())
            # print(value.all != getattr(self, 'so_executors').all)
        # result.update({name: getattr(self, name) for name, value in self._original_values.items() if
        #                value != getattr(self, name)})
        # result.update(
        #     {'so_executors': [so_executor for so_executor in self._original_values.get('so_executors').all() if
        #                       'so_executors' in self._original_values.keys()]})
        # if getattr(self, 'so_executors').all():
        #     # print(self._original_values.items())
        #     # print(self._original_values.get('so_executors').all())
        #     # print(getattr(self, 'so_executors').all())
        #     temp = {}
        #     so_executors = [so_executor for so_executor in getattr(self, 'so_executors').all()]
        #     temp['so_executors'] = so_executors
        #     result.update(temp)
        # print(result.get('so_executors'))
        return result
