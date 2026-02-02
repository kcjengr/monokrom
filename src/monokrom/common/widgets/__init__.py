from qtpyvcp.widgets.qtdesigner import _DesignerPlugin
from .mk_line_edit import MyLineEdit
from .mk_push_button import MkPushButton
from .mk_dro import MonokromDroWidget, MonokromDroGroup
from .mdi_entry import MkMdiEntry
from .file_list_view import MkFileTableView
from .recent_file_list_view import MkRecentFileListView
from .file_list_view import MkRemovableDeviceComboBox
from .transparent_widget import MkTransparentWidget
from .group_box import MkGroupBox
from .tab_widget import MkTabWidget
from .mk_led_hal import MkHalLedIndicator
from .mk_led import MkLedIndicator

class MyLineEdit_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MyLineEdit

class MkPushButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkPushButton

class MkDroWidget_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MonokromDroWidget

class MkDroGroup_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MonokromDroGroup

class MkMdiEntry_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkMdiEntry

class MkFileTableView_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkFileTableView

class MkRecentFileListView_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkRecentFileListView

class MkRemovableDeviceComboBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkRemovableDeviceComboBox

class MkTransparentWidget_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkTransparentWidget
    def isContainer(self):
        return True

class MkGroupBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkGroupBox
    def isContainer(self):
        return True
    def domXml(self):
        return """<widget class="MkGroupBox" name="groupbox">
                  <property name="title">
                    <string>MkGroupBox</string>
                  </property>
                  </widget>"""

class MkTabWidget_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkTabWidget
    def isContainer(self):
        return True
    def domXml(self):
        return """<widget class="MkTabWidget" name="tabwidget">
                    <property name="geometry">
                     <rect>
                      <x>0</x>
                      <y>0</y>
                      <width>250</width>
                      <height>200</height>
                     </rect>
                    </property>
                    <widget class="QWidget" name="tab_1">
                     <attribute name="title">
                      <string>Page 1</string>
                     </attribute>
                    </widget>
                  </widget>"""

class MkHalLedIndicator_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkHalLedIndicator
    
class MkLedIndicator_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkLedIndicator
