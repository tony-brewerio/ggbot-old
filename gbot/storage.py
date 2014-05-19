

class Storage(dict):

    def get_set(self, key, default):
        self[key] = self.get(key, default)
        return self[key]



storage = Storage()