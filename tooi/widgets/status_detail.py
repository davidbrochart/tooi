from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from tooi.entities import MediaAttachment, Status
from tooi.utils.datetime import format_datetime
from tooi.widgets.account import AccountHeader
from tooi.widgets.link import Link
from tooi.widgets.markdown import Markdown
from tooi.widgets.poll import Poll


class StatusDetail(VerticalScroll):
    DEFAULT_CSS = """
    #status_detail {
        width: 2fr;
        padding: 0 1;
    }
    #status_detail:focus {
        background: $panel;
    }
    .status_content {
        margin-top: 1;
    }
    .status_sensitive {
        display: none;
        height: auto;
    }
    .status_revealed {
        display: none;
        height: auto;
    }
    .spoiler_text {
        margin-top: 1;
    }
    .sensitive_notice {
        margin-top: 1;
        color: red;
        border: solid red;
    }
    """

    BINDINGS = [
        Binding("up,k", "scroll_up", "Scroll Up", show=False),
        Binding("down,j", "scroll_down", "Scroll Down", show=False),
        Binding("home", "scroll_home", "Scroll Home", show=False),
        Binding("end", "scroll_end", "Scroll End", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
    ]

    def __init__(self, status: Status, revealed: bool = False):
        super().__init__(id="status_detail")
        self.status = status
        self.sensitive = status.original.sensitive
        self.revealed = revealed

    def compose(self):
        status = self.status.original

        if self.status.reblog:
            yield BoostedBy(self.status)

        hide_sensitive = self.sensitive and not self.revealed
        sensitive_classes = "status_sensitive " + ("show" if hide_sensitive else "hide")
        revealed_classes = "status_revealed " + ("hide" if hide_sensitive else "show")

        yield AccountHeader(status.account)
        yield Vertical(*self.compose_sensitive(status), classes=sensitive_classes)
        yield Vertical(*self.compose_revealed(status), classes=revealed_classes)
        yield StatusMeta(status)

    def reveal(self):
        if self.sensitive and not self.revealed:
            self.query_one(".status_sensitive").styles.display = "none"
            self.query_one(".status_revealed").styles.display = "block"
            self.revealed = True

    def compose_sensitive(self, status: Status) -> ComposeResult:
        if status.spoiler_text:
            yield Static(status.spoiler_text, classes="spoiler_text")

        yield Static("Marked as sensitive. Press S to view.", classes="sensitive_notice")

    def compose_revealed(self, status: Status) -> ComposeResult:
        if status.spoiler_text:
            yield Static(status.spoiler_text, classes="spoiler_text")

        yield Markdown(status.content_md, classes="status_content")

        if status.poll:
            yield Poll(status.poll)

        if status.card:
            yield StatusCard(status)

        for attachment in status.original.media_attachments:
            yield StatusMediaAttachment(attachment)


class BoostedBy(Static):
    DEFAULT_CSS = """
    BoostedBy {
        color: gray;
        border-bottom: ascii gray;
    }
    """

    def __init__(self, status: Status):
        self.status = status
        super().__init__()

    def render(self):
        return f"boosted by {self.status.account.acct}"


class StatusCard(Widget):
    DEFAULT_CSS = """
    .card {
        border: round white;
        padding: 0 1;
        height: auto;
        margin-top: 1;
    }

    .card > .title {
        text-style: bold;
    }
    """

    def __init__(self, status: Status):
        self.status = status
        super().__init__(classes="card")

    def compose(self):
        card = self.status.original.card

        if not card:
            return

        yield Link(card.url, card.title, classes="title")

        if card.author_name:
            yield Static(f"by {card.author_name}")

        if card.description:
            yield Static("")
            yield Static(card.description)

        yield Static("")
        yield Link(card.url)


class StatusMediaAttachment(Widget):
    DEFAULT_CSS = """
    .media_attachment {
        border-top: ascii gray;
        height: auto;
    }

    .media_attachment > .title {
        text-style: bold;
    }
    """

    attachment: MediaAttachment

    def __init__(self, attachment: MediaAttachment):
        self.attachment = attachment
        super().__init__(classes="media_attachment")

    def compose(self):
        yield Static(f"Media attachment ({self.attachment.type})", classes="title")
        if self.attachment.description:
            yield Static(self.attachment.description)
        yield Link(self.attachment.url)


class StatusMeta(Static):
    DEFAULT_CSS = """
    .meta {
        color: gray;
        border-top: ascii gray;
    }
    """

    status: Status

    def __init__(self, status: Status):
        self.status = status
        super().__init__(classes="meta")

    def render(self):
        status = self.status.original
        parts = [
            f"[bold]{format_datetime(status.created_at)}[/]",
            f"{status.reblogs_count} boosts",
            f"{status.favourites_count} favourites",
            f"{status.replies_count} replies",
            f"{status.visibility.capitalize()}",
        ]
        return " · ".join(parts)


class StatusDetailPlaceholder(Static, can_focus=True):
    DEFAULT_CSS = """
    #status_detail {
        width: 2fr;
        padding: 0 1;
        color: gray;
        height: 100%;
    }
    #status_detail:focus {
        background: $panel;
    }
    """

    def __init__(self):
        super().__init__("No status selected", id="status_detail")

    def show_sensitive(self):
        pass
