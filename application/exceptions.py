
class userNotFoundError(Exception):
    pass


class invaldPasswordError(Exception):
    pass


class invalidSymbolError(Exception):
    def __init__(self, msg='Invalid symbol', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class zeroTransactionError(Exception):
    def __init__(self, msg="You can't trade less than one", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)