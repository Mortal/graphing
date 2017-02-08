from cairo import Context as _Context


class ContextMeta(type):
    def __subclasscheck__(cls, subclass):
        if subclass is _Context:
            return True
        return super().__subclasscheck__(subclass)

    def __instancecheck__(cls, instance):
        if type(instance) is _Context:
            return True
        return super().__instancecheck__(subclass)


class Context(_Context, metaclass=ContextMeta):
