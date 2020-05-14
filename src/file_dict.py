import os
import ujson



class JSONSerializer:
    @staticmethod
    def pack(data):
        return ujson.dumps(data).encode()

    @staticmethod
    def unpack(data):
        decoded = data.decode() if isinstance(data, bytes) else data
        return ujson.loads(decoded)

class FileDict:
    """Persistent dict-like storage on a disk accessible by obj['item_name']"""

    def __init__(self, filename):
        self.filename = filename.replace(':', '_')
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        self.cache = {}
        self.serializer = JSONSerializer

    def __getitem__(self, name):
        key = str(name)
        if key not in self.cache:
            try:
                content = self._get_file_content()
                if key not in content:
                    raise KeyError

            except FileNotFoundError:
                open(self.filename, 'w+b').close()
                raise KeyError

            else:
                self.cache = content

        return self.cache[key]

    def __setitem__(self, name, value):
        try:
            content = self._get_file_content()
        except FileNotFoundError:
            content = {}

        if not isinstance(name, str):
            # hack to use objects as keys
            # convert key to json string
            key = str(ujson.dumps(name))
        else:
            key = name

        content.update({key: value})
        with open(self.filename, 'w+b') as f:
            f.write(self.serializer.pack(content))

        self.cache = content

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
            yield ujson.loads(key), value

    def clear(self):
        self.cache = {}
        open(self.filename, 'w').close()
