
from resources import constants, device_probe, utilities
from resources.build import support
from data import model_array, smbios_data, cpu_data


class build_security:

    def __init__(self, model, versions, config):
        self.model = model
        self.constants: constants.Constants = versions
        self.config = config
        self.computer = self.constants.computer


    def build(self):
        return