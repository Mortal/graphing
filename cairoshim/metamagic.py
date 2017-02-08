def superclass_of(t):
    def subclasscheck(cls, subclass):
        if subclass is t:
            return True
        return super(superclass_of_t, cls).__subclasscheck__(subclass)

    def instancecheck(cls, instance):
        if type(instance) is t:
            return True
        return super(superclass_of_t, cls).__instancecheck__(instance)

    superclass_of_t = type(
        'superclass_of_%s' % t.__name__, (type,),
        dict(__subclasscheck__=subclasscheck,
             __instancecheck__=instancecheck))

    return superclass_of_t
