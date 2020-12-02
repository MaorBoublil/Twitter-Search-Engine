class ConfigClass:
    output_path=''

    @staticmethod
    def set_path(path):
        ConfigClass.output_path = path

    @staticmethod
    def get_path():
        return ConfigClass.output_path
