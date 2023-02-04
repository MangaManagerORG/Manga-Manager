from src.MetadataManager.GUI.widgets import OptionMenuWidget, LongTextWidget, ComboBoxWidget


class WidgetManager:
    cinfo_tags: list[str] = list()

    def get_widget(self, name) -> ComboBoxWidget | LongTextWidget | OptionMenuWidget:
        return getattr(self, name)

    def add_widget(self, name, widget_frame: ComboBoxWidget | LongTextWidget | OptionMenuWidget):
        self.cinfo_tags.append(name)
        setattr(self, name, widget_frame)

    def __setattr__(self, key, value):
        self.cinfo_tags.append(key)
        object.__setattr__(self, key, value)

    def clean_widgets(self):
        for widget_name in self.__dict__:
            widget = self.get_widget(widget_name)
            widget.set_default()
            if isinstance(widget, ComboBoxWidget):
                widget.widget['values'] = widget.default_vals or []

    def toggle_widgets(self,enabled=True):
        for widget_name in self.__dict__:
            widget = self.get_widget(widget_name)
            if isinstance(widget, OptionMenuWidget):
                widget.widget_slave.configure(state="normal" if enabled else "disabled")
            elif isinstance(widget, LongTextWidget):
                # widget.widget_slave.configure(state="normal" if enabled else "readonly")
                pass
            else:
                widget.widget.configure(state="normal" if enabled else "disabled")

    def get_tags(self):
        return [tag for tag in self.cinfo_tags]