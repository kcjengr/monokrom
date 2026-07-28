"""MDI panel service for G-code entry assistance."""


class MdiPanelService:
    """Manages MDI panel interactions for G-code entry assistance.

    Provides helpers for building MDI commands via button clicks, looking up
    available parameters for known G-code words, and text editing operations.
    """

    def __init__(self, main_window):
        self.main_window = main_window

    # -- Public API -----------------------------------------------------------

    def append_char(self, char):
        """Append a character to the MDI entry text.

        Args:
            char: Single character string to append.
        """
        text = self.main_window.mdiEntry.text() + char
        self.main_window.mdiEntry.setText(text)

    def clear_params(self):
        """Clear all parameter buttons (btnGcodeP1 through btnGcodeP10)."""
        for index in range(1, 11):
            getattr(self.main_window, 'btnGcodeP' + str(index)).setText('')

    def lookup_params(self, gcode_text):
        """Look up available parameters for a G-code word and update param buttons.

        Args:
            gcode_text: G-code word string (e.g., 'G1', 'G2', 'M3').

        Returns:
            True if the G-code word was found and params were set, False otherwise.
        """
        import monokrom.plasma.mdi_text as mdiText

        if not gcode_text:
            self.clear_params()
            return False

        words = mdiText.gcode_words()
        if gcode_text in words:
            self.clear_params()
            for index, value in enumerate(words[gcode_text], start=1):
                getattr(self.main_window, 'btnGcodeP' + str(index)).setText(value)
            return True
        else:
            self.clear_params()
            return False

    def backspace(self):
        """Remove the last character from the MDI entry text."""
        text = self.main_window.mdiEntry.text()
        if len(text) > 0:
            text = text[:-1]
            self.main_window.mdiEntry.setText(text)

    def add_space(self):
        """Append a space to the MDI entry text if it has content."""
        text = self.main_window.mdiEntry.text()
        if text:
            text += ' '
            self.main_window.mdiEntry.setText(text)
