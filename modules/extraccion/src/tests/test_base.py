from collections import defaultdict
import gc

from modules.extraccion.src.File import ExtractorFile


class EmptyConfig(Exception):
    pass
class EmptyFile(Exception):
    pass


class TestExtractor:
    def __init__(self, extractor_file: ExtractorFile):
        self.extractor_file = extractor_file
        self.status = "🕓 Pendiente"
        self.log = ""
        self.errors = {}

    def run(self):
        raise NotImplementedError("Debes implementar run()")

    def clear(self):
        self.config_content = None
        self.file_content = None
        if hasattr(self.extractor_file, "unload_file_content"):
            self.extractor_file.unload_file_content()
        gc.collect()

    def launch_ok(self, log):
        self.status = "✔️ OK"
        self.log = log

    def launch_error(self, log):
        self.status = "❌ Error"
        self.log += f'{log}\n'

    def launch_warning(self, log):
        self.status = "⚠️ Warning"
        self.log += f'{log}\n'

    def convertir_a_dict(self, obj):
        if isinstance(obj, defaultdict):
            return {k: self.convertir_a_dict(v) for k, v in obj.items()}
        elif isinstance(obj, dict):
            return {k: self.convertir_a_dict(v) for k, v in obj.items()}
        else:
            return obj


