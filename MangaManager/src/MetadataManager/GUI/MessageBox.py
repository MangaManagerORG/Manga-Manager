from typing import Type

from src.MetadataManager.GUI.OneTimeMessageBox import OneTimeMessageBox
from src.MetadataManager.GUI.widgets.MessageBoxWidget import MessageBoxWidget, MessageBoxButton


class MessageBoxWidgetFactory:
    """
    A factory that generates predefined widgets. Return values /buttons are predefined (NO, YES, CANCEL)
    """

    @staticmethod
    def yes_or_no(parent, title, description):
        ret = MessageBoxWidget(parent) \
            .with_title(title) \
            .with_icon(MessageBoxWidget.icon_question) \
            .with_description(description) \
            .with_actions([MessageBoxButton(0, "No"), MessageBoxButton(1, "Yes")])
        return ret.prompt()

    @staticmethod
    def showerror(parent, title, description):
        ret = MessageBoxWidget(parent) \
            .with_title(title) \
            .with_icon(MessageBoxWidget.icon_error) \
            .with_description(description) \
            .with_actions([MessageBoxButton(1, "Ok")])

        return ret.prompt()

    @staticmethod
    def showwarning(parent, title, description):
        ret = MessageBoxWidget(parent) \
            .with_title(title) \
            .with_icon(MessageBoxWidget.icon_warning) \
            .with_description(description) \
            .with_actions([MessageBoxButton(1, "Ok")])
        return ret.prompt()

    @staticmethod
    def get_onetime_messagebox() -> Type[OneTimeMessageBox]:
        return OneTimeMessageBox

    @staticmethod
    def get_box_button() -> Type[MessageBoxButton]:
        return MessageBoxButton

