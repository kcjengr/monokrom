import pytest


@pytest.fixture
def app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


class TestMyLineEdit:
    def test_default_text(self, app):
        from monokrom.common.widgets.mk_line_edit import MyLineEdit

        widget = MyLineEdit()
        assert widget.text() == "MyLineEdit"
        widget.deleteLater()

    def test_set_text(self, app):
        from monokrom.common.widgets.mk_line_edit import MyLineEdit

        widget = MyLineEdit()
        widget.setText("hello")
        assert widget.text() == "hello"
        widget.deleteLater()

    def test_clear(self, app):
        from monokrom.common.widgets.mk_line_edit import MyLineEdit

        widget = MyLineEdit()
        widget.clear()
        assert widget.text() == ""
        widget.deleteLater()

    def test_set_placeholder_text(self, app):
        from monokrom.common.widgets.mk_line_edit import MyLineEdit

        widget = MyLineEdit()
        widget.setPlaceholderText("enter value")
        assert widget.placeholderText() == "enter value"
        widget.deleteLater()

    def test_echo_mode(self, app):
        from PySide6.QtWidgets import QLineEdit
        from monokrom.common.widgets.mk_line_edit import MyLineEdit

        widget = MyLineEdit()
        widget.setEchoMode(QLineEdit.Password)
        assert widget.echoMode() == QLineEdit.Password
        widget.deleteLater()


class TestMkPushButton:
    def test_default_text(self, app):
        from monokrom.common.widgets.mk_push_button import MkPushButton

        widget = MkPushButton()
        assert widget.text() == "MkPushButton"
        widget.deleteLater()
