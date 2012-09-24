import collections


class HeaderDict(object):
    """
    A dict-like class for managing HTTP headers. Data is stored ordered and
    can contain multiple duplicate keys. Lookups are case-insenstive.
    """
    
    def __init__(self):
        self.__items = []
    
    def __getitem__(self, key):
        ikey = key.lower()
        for k, v in self.__items:
            if k.lower() == ikey:
                return v
        raise KeyError(key)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def iteritems(self, lower=False):
        for key, value in self:
            if lower:
                key = key.lower()
            yield key, value
    
    def items(self, lower=False):
        return list(self.iteritems(lower))
    
    def __delitem__(self, key):
        key = key.lower()
        new = []
        for k, v in self.__items:
            if k.lower() != key:
                new.append((k, v))
        self.__items[:] = new
    
    def __iter__(self):
        return iter(self.__items)
    
    def add(self, key, value):
        self._validate_value(value)
        self.__items.append((key, value))
    
    def _validate_value(self, value):
        if isinstance(value, basestring):
            if "\n" in value or "\r" in value:
                raise ValueError("Detected newline in header value. This is "
                    "a potential security problem.")
    
    def set(self, key, value):
        """
        Remove all header tuples for `key` and add a new one. The newly added
        key either appears at the end of the list if there was no entry or
        replaces the first one.
        """
        self._validate_value(value)
        if not self.__items:
            self.__items.append((key, value))
            return
        itemiter = iter(self.__items)
        ikey = key.lower()
        for idx, (okey, ovalue) in enumerate(itemiter):
            if okey.lower() == ikey:
                self.__items[idx] = (key, value)
                break
        else:
            self.__items.append((key, value))
            return
        self.__items[idx+1:] = [t for t in itemiter if t[0].lower() !=  ikey]
    
    def __setitem__(self, key, value):
        self.set(key, value)
