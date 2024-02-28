import abc


class IMMExtension(abc.ABC):
    """
        The basic interface that all extensions must implement. An extension is functionality that can be added and
        dynamically loaded into Manga Manager. An extension can optionally offer settings to the user to configure.
    """

    """
       A set of settings which will be found in the main settings dialog of Manga Manager and used for the source
    """
    settings = []
    # Version of the extension
    version = '0.0.0.0'
    # Name of the Extension
    name = ''

    def save_settings(self):
        """
        When a setting update occurs, this is invoked and internal state should be updated from Settings()
        """
        pass
