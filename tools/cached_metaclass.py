# coding: utf-8


class Cached(type):
    """Cache metaclass for BaseObj.

    the cache key is db_mapping.
    """

    def __call__(self, context, db_mapping, *args, **kwargs):
        if context:
            if db_mapping in context.cached_dict:
                return context.cached_dict[db_mapping]
            obj = super(Cached, self).__call__(context, db_mapping, *args, **kwargs)
            context.cached_dict[db_mapping] = obj
            return obj
        return super(Cached, self).__call__(context, db_mapping, *args, **kwargs)
