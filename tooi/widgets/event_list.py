from textual.widgets import ListItem, Label

from tooi.data.events import Event, NotificationEvent, StatusEvent
from tooi.context import get_context
from tooi.entities import Account
from tooi.messages import EventHighlighted, EventSelected
from tooi.utils.datetime import format_datetime, format_relative
from tooi.widgets.list_view import ListView


class EventList(ListView):
    """
    A ListView that shows a list of events.
    """

    # When prepending events, if we have more than this many events, start removing events from the
    # end.
    MAX_LENGTH = 1024

    DEFAULT_CSS = """
    EventList {
        width: 1fr;
        min-width: 20;
        border-right: solid $accent;
    }
    EventList:focus-within {
        background: $panel;
    }
    """

    def __init__(self, events: list[Event]):
        super().__init__()
        self.append_events(events)

    @property
    def current(self) -> Event | None:
        if self.highlighted_child is None:
            return None

        return self.highlighted_child.event

    def replace(self, next_events: list[Event]):
        self.clear()
        self.append_events(next_events)

    def append_events(self, next_events: list[Event]):
        for event in next_events:
            self.mount(EventListItem(event))

        if self.highlighted_child is None:
            self.index = 0

        if self.current is not None:
            self.post_message(EventHighlighted(self.current))

    def prepend_events(self, next_events: list[Event]):
        for event in next_events:
            self.mount(EventListItem(event), before=0)

        if self.current is None:
            self.index = 0
        else:
            self.index += len(next_events)

        if self.current is not None:
            self.post_message(EventHighlighted(self.current))

        for item in self.query(EventListItem)[self.MAX_LENGTH:]:
            item.remove()

    def focus_event(self, event_id: str):
        for i, item in enumerate(self.query(EventListItem)):
            if item.event.id == event_id:
                self.index = i

    def refresh_events(self):
        for item in self.query(EventListItem):
            item.refresh_event()

    @property
    def count(self):
        return len(self)

    def on_list_view_highlighted(self, message: ListView.Highlighted):
        if message.item:
            self.post_message(EventHighlighted(message.item.event))

    def on_list_view_selected(self, message: ListView.Highlighted):
        if self.current:
            self.post_message(EventSelected(self.current))


class EventListItem(ListItem, can_focus=True):
    event: Event

    DEFAULT_CSS = """
    EventListItem {
        layout: horizontal;
        width: auto;
    }

    Label {
        width: 1fr;
        align: left middle;
    }

    .event_list_timestamp {
        width: auto;
        min-width: 4;
    }

    .event_list_acct {
        color: green;
        width: auto;
        padding-left: 1;
    }

    .event_list_flags {
        width: 2;
        padding-left: 1;
    }
    """

    NOTIFICATION_FLAGS = {
        "mention": "@",
        "reblog": "B",
        "favourite": "*",
        "follow": ">",
    }

    def __init__(self, event: Event):
        super().__init__(classes="event_list_item")
        self.event = event
        self.ctx = get_context()

    def compose(self):
        yield Label(self.format_timestamp(), classes="event_list_timestamp")
        yield Label(self._format_flags(), classes="event_list_flags")
        yield Label(self._format_account_name(self.event.account), classes="event_list_acct")

    def format_timestamp(self):
        if self.ctx.config.relative_timestamps:
            return format_relative(self.event.created_at)
        else:
            return format_datetime(self.event.created_at)

    def refresh_event(self):
        # Don't use query_one since the timestamp might not exist if we're updated before we've had
        # a chance to render.
        for label in self.query(".event_list_timestamp"):
            label.update(self.format_timestamp())

    def _format_account_name(self, account: Account) -> str:
        ctx = get_context()
        acct = account.acct
        return acct if "@" in acct else f"{acct}@{ctx.auth.domain}"

    def _format_flags(self) -> str:
        match self.event:
            case StatusEvent():
                return "B" if self.event.status.reblog else " "
            case NotificationEvent():
                return self.NOTIFICATION_FLAGS.get(self.event.notification.type, " ")
            case _:
                return " "
