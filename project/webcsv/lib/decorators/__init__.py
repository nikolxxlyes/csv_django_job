class classproperty(property):
    def __get__(self, obj, objtype=None):
        return super().__get__(objtype)