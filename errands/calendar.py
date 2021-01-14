import pytz
from datetime import datetime

from django_ical.views import ICalFeed
from errands.models import Tasks, Boards


class EventFeed(ICalFeed):
    """
    A simple event calender
    """
    product_id = '-//example.com//Example//EN'
    timezone = 'UTC'
    file_name = "Calendar.ics"

    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.board_id = kwargs['pk']
        return super(EventFeed, self).__call__(request, *args, **kwargs)

    def items(self):
        return Tasks.objects.filter(board_id=self.board_id, status__in=('В работе', 'Требуется помощь'),
                                    responsible=self.request.user).order_by(
            '-term')

    def item_guid(self, item):
        return f"{item.id}{'global_name'}"

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

    def item_start_datetime(self, item):
        return datetime.now(pytz.utc)

    def item_end_datetime(self, item):
        return item.term

    def item_link(self, item):
        return f"https://todo.admlr.lipetsk.ru/board/{self.board_id}/"
