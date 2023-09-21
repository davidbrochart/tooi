from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Markdown, Pretty, Static

from tooi.entities import ExtendedDescription, Instance, InstanceV2


class InstanceScreen(Screen[None]):
    DEFAULT_CSS = """
    #instance_screen {
    }
    """

    def __init__(
        self,
        *,
        instance: Instance | None = None,
        instance_v2: InstanceV2 | None = None,
        description: ExtendedDescription | None = None,
    ):
        self.instance = instance
        self.instance_v2 = instance_v2
        self.description = description
        super().__init__(id="instance_screen")

    def compose(self) -> ComposeResult:
        yield VerticalScroll(*self.compose_items())

    def compose_items(self) -> ComposeResult:
        # Fall back to instance v1 if v2 is not available
        if self.instance_v2:
            yield from self.compose_instance_v2(self.instance_v2)
        elif self.instance:
            yield from self.compose_instance(self.instance)

        if self.description:
            yield from self.compose_description(self.description)

    def compose_instance_v2(self, instance: InstanceV2):
        yield Static(instance.title)
        yield Static(instance.domain)

        yield Static("")
        yield Static(instance.description)

        yield Static("")
        yield Static(f"Contact: {instance.contact.email}")

        yield Static("")
        yield Static("Rules:")
        for rule in instance.rules:
            yield Static(f"* {rule.text}")

    def compose_instance(self, instance: Instance):
        yield Static("TODO: Intance goes here")

    def compose_description(self, description: ExtendedDescription):
        yield Static("")
        yield Markdown(description.content_md)
