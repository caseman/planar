
def cached_property(func):

    def getter(self, name=func.func_name):
        try:
            return self.__dict__[name]
        except KeyError:
            self.__dict__[name] = value = func(self)
            return value
    
    getter.func_name = func.func_name
    return property(getter, doc=func.func_doc)

# vim: ai ts=4 sts=4 et sw=4 tw=78

