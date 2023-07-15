from functools import wraps
import logging
import traceback
import inspect


def log(logger):
    '''
    Decorator to log function calls
    '''
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)
            logger.debug(
                f'Function {func.__name__} called with parameters {args}, {kwargs}. '
                f'from function {traceback.format_stack()[0].strip().split()[-1]} of module {func.__module__}.'
                f'Call from function {inspect.stack()[1][3]}')
            return res
        return decorated
    return decorator


def login_required(func):
    '''
    Decorator to check if client is logged in.
    If User is not logged in raises TypeError exception.
    '''

    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр Server
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from server import Server
        if isinstance(args[0], Server):
            found = False
            # Проверяем, что сокет есть в списке present_users класса Server
            for client in args[0].present_users.keys():
                if args[0].present_users[client] in args[3]:
                    found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if 'action' in arg and arg['action'] == 'presence':
                        found = True
            # Если не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)
    return checker
