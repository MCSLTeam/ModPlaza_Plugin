from Adapters.Plugin import Plugin

ModPlaza_Plugin = Plugin()


def load():
    pass


def enable():
    pass


def disable():
    pass


ModPlaza_Plugin.register_loadFunc(load)
ModPlaza_Plugin.register_enableFunc(enable)
ModPlaza_Plugin.register_disableFunc(disable)
