import inspect


class AutoLogMeta(type):
    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if inspect.isfunction(attr_value) and attr_name != '__init__':
                has_logger_param = 'autologger' in inspect.signature(attr_value).parameters
                attrs[attr_name] = cls.decorate_method(attr_name, attr_value, has_logger_param)

        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def decorate_method(method_name: str, method: callable, has_logger_param: bool):
        def wrapper(cls, *args, **kwargs):
            _isExtend: bool = method.__annotations__.get('__extent__')
            _isSilent: bool = method.__annotations__.get('__silent__')

            def _logger(msg: str):
                print(f"[{cls.__class__.__name__}::{method_name}] \t{msg}")

            if _isSilent is None:
                """ normal method """
                if has_logger_param and _isExtend:
                    kwargs['autologger'] = _logger

                print(f"[{cls.__class__.__name__}::{method_name}] {method.__annotations__.get('__before__', '!!!')}")
                ret = method(cls, *args, **kwargs)
                print(f"[{cls.__class__.__name__}::{method_name}] {method.__annotations__.get('__after__', '!!!')}")
                return ret

            elif _isSilent:
                """ keep logger silent """
                if has_logger_param and _isExtend:
                    kwargs['autologger'] = lambda: ()
                return method(cls, *args, **kwargs)

            else:
                """ func hook decorator used """
                if has_logger_param and _isExtend:
                    kwargs['autologger'] = _logger

                print(f"[{cls.__class__.__name__}::{method_name}] {method.__annotations__.get('__before__', '!!!')}")
                ret = method(cls, *args, **kwargs)
                print(f"[{cls.__class__.__name__}::{method_name}] {method.__annotations__.get('__after__', '!!!')}")
                return ret

        return wrapper


def extend(func: callable) -> callable:
    func.__annotations__['__extent__'] = True
    func.__annotations__['__silent__'] = False
    return func


def funchook(silent: bool = False, before: str = '', after: str = '') -> callable:
    def decorator(func: callable) -> callable:
        def wrapper(*args, **kwargs):
            if AutoLogMeta not in [type(cls) for cls in args[0].__class__.mro()]:
                print(before)
                ret = func(*args, **kwargs)
                print(after)
            else:
                if silent:
                    func.__annotations__['__silent__'] = True
                    return func

                func.__annotations__['__silent__'] = False
                func.__annotations__['__before__'] = before
                func.__annotations__['__after__'] = after
                ret = func(*args, **kwargs)
            return ret

        return wrapper

    return decorator


def silent(func: callable) -> callable:
    func.__annotations__['__silent__'] = True
    return func
