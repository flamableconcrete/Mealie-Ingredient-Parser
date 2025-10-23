"""Session resume modal for resuming previous batch processing sessions."""

from loguru import logger
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from mealie_parser.models.session_state import SessionState


class SessionResumeModal(ModalScreen[bool]):
    """
    Modal dialog for resuming a previous session.

    Displays session information and allows user to choose between
    resuming the previous session or starting fresh.

    Attributes
    ----------
    session_state : SessionState
        The previous session state to potentially resume
    """

    CSS = """
    SessionResumeModal {
        align: center middle;
    }

    #dialog {
        width: 80;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        height: auto;
    }

    #session-info {
        background: $boost;
        padding: 1;
        margin: 1 0;
        height: auto;
    }

    #message {
        text-align: center;
        margin: 1 0;
        height: auto;
    }

    #buttons {
        layout: horizontal;
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("r", "resume", "Resume"),
        ("n", "new", "Start Fresh"),
        ("escape", "new", "Start Fresh"),
    ]

    def __init__(self, session_state: SessionState):
        """
        Initialize session resume modal.

        Parameters
        ----------
        session_state : SessionState
            The previous session state
        """
        super().__init__()
        self.session_state = session_state
        logger.debug(f"Initialized SessionResumeModal with session: {session_state.session_id}")

    def compose(self) -> ComposeResult:
        """Build the modal UI."""
        with Container(id="dialog"):
            yield Static("Previous Session Found", id="title")

            # Session information
            session_info = self._build_session_info()
            yield Static(session_info, id="session-info")

            # Message
            yield Static("Would you like to resume where you left off?", id="message")

            # Buttons
            with Horizontal(id="buttons"):
                yield Button("Resume Session (r)", id="resume", variant="primary")
                yield Button("Start Fresh (n)", id="new")

    def _build_session_info(self) -> str:
        """
        Build session information summary.

        Returns
        -------
        str
            Formatted session information
        """
        lines = [
            f"Session ID: {self.session_state.session_id[:16]}...",
            f"Mode: {self.session_state.mode.capitalize()}",
            f"Last Updated: {self.session_state.last_updated[:19]}",
            "",
            "Progress:",
            f"  • Processed: {len(self.session_state.processed_patterns)} patterns",
            f"  • Skipped: {len(self.session_state.skipped_patterns)} patterns",
            f"  • Units Created: {len(self.session_state.created_units)}",
            f"  • Foods Created: {len(self.session_state.created_foods)}",
        ]

        # Add current operation if exists
        if self.session_state.current_operation:
            op = self.session_state.current_operation
            lines.extend(
                [
                    "",
                    f"In Progress: {op.get('operation_type', 'Unknown')} - {op.get('pattern_text', 'N/A')}",
                ]
            )

        return "\n".join(lines)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "resume":
            logger.info(f"User chose to resume session: {self.session_state.session_id}")
            self.dismiss(True)
        elif event.button.id == "new":
            logger.info("User chose to start fresh session")
            self.dismiss(False)

    def action_resume(self) -> None:
        """Resume session action."""
        logger.info(f"Resuming session: {self.session_state.session_id}")
        self.dismiss(True)

    def action_new(self) -> None:
        """Start new session action."""
        logger.info("Starting fresh session")
        self.dismiss(False)
