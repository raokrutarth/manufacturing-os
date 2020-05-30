import os
import jsonpickle
from atomicfile import AtomicFile


BASE_DIR = './tmp/'


class ComplexJSONSerializer:
    @staticmethod
    def pack(data):
        return jsonpickle.dumps(data, indent=4)

    @staticmethod
    def unpack(data):
        decoded = data.decode() if isinstance(data, bytes) else data
        return jsonpickle.loads(decoded)


class FileDict:
    """Persistent dict-like storage on a disk accessible by obj['item_name']"""

    def __init__(self, filename):
        self.filename = os.path.join(BASE_DIR, filename.replace(':', '_'))
        if self.filename[-4:] != '.log':
            self.filename += '.log'
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        self.write_mode = 'w'
        self.read_mode = 'r'

        self.serializer = ComplexJSONSerializer

    def __getitem__(self, name):
        key = self.process_key(name)
        content = self._get_file_content()
        if key not in content:
            raise KeyError
        return content[key]

    @staticmethod
    def process_key(name):
        if not isinstance(name, (str, int)):
            # hack to use objects as keys - convert key to json string
            # jsonpickle allows encoding complex python classes
            key = str(jsonpickle.dumps(name))
        else:
            key = name
        return key

    def __setitem__(self, name, value):
        try:
            content = self._get_file_content()
        except FileNotFoundError:
            content = {}

        key = self.process_key(name)

        content.update({key: value})
        with AtomicFile(self.filename, self.write_mode) as f:
            f.write(self.serializer.pack(content))
            f.close()

    def update(self, updates):
        try:
            content = self._get_file_content()
        except FileNotFoundError:
            content = {}

        mod_updates = {self.process_key(key): value for key, value in updates.items()}
        content.update(mod_updates)

        with AtomicFile(self.filename, self.write_mode) as f:
            f.write(self.serializer.pack(content))
            f.close()

    def _get_file_content(self):
        try:
            with open(self.filename, self.read_mode) as f:
                content = f.read()
                if not content:
                    return {}

            return self.serializer.unpack(content)
        except FileNotFoundError:
            return {}

    def items(self):
        contents = self._get_file_content()
        for key, value in contents.items():
            yield jsonpickle.loads(key), value

    def clear(self):
        AtomicFile(self.filename, self.write_mode).close()
