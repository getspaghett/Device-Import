import platform
import dmidecode

class HardwareInfo:
    def __init__(self):
        self.platform = platform.platform()
        self.arch = platform.machine()
        self.processor = platform.processor()
        self.version = platform.version()
        self.node = platform.node()
        self.dmi = None

    def __str__(self):
        return f'Platform: {self.platform}\nArch: {self.arch}\nProcessor: {self.processor}\nVersion: {self.version}\nNode: {self.node}'

    def getDmiInfo(self):
        self.dmi
        # dmidecode.DebugDMIDecode() is a custom function that runs dmidecode with sudo
        # change to dmidecode.DMIDecode() if you don't need to use sudo
        self.dmi = dmidecode.DebugDMIDecode()
        return self.dmi

