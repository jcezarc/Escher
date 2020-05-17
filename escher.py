class BaseGenerator:
    def render_code(self, params):
        path = params['path']
        file_name = params['file_name']
        write_mode = params.get('write_mode', True)
        values = params['values']
        pass
    def empty_dir(self, target):
        pass
    def create_folders(self):
        pass
    def copy_util(self, ignore_list):
        pass
    def build_app(self):
        pass

