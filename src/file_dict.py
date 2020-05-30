import os
import jsonpickle
from atomicfile import AtomicFile


BASE_DIR = './tmp/'


class ComplexJSONSerializer:
    @staticmethod
    def pack(data):
        return jsonpickle.dumps(data).encode()

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

        self.serializer = ComplexJSONSerializer

    def __getitem__(self, name):
        key = str(name)
        content = self._get_file_content()
        if key not in content:
            raise KeyError
        return content[key]

    def __setitem__(self, name, value):
        try:
            content = self._get_file_content()
        except FileNotFoundError:
            content = {}

        if not isinstance(name, str):
            # hack to use objects as keys - convert key to json string
            # jsonpickle allows encoding complex python classes
            key = str(jsonpickle.dumps(name))
        else:
            key = name

        content.update({key: value})
        with AtomicFile(self.filename, "w+b") as f:
            f.write(self.serializer.pack(content))
            f.close()

    def _get_file_content(self):
        try:
            with open(self.filename, 'rb') as f:
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
        AtomicFile(self.filename, 'w+b').close()
