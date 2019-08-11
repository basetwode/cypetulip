class JsonResponse():
    errors = []
    success = True

    def __init__(self, errors=[], success=True, next_url='', token=""):
        self.errors = errors
        self.success = success
        self.next_url = next_url
        self.token = token

    def dump(self):
        self_dump = self.__dict__.copy()
        self_dump['errors'] = [error.dump() for error in self.errors]
        return self_dump

    def add_error(self, error):
        self.errors.append(error)


class Error():
    def __init__(self, code, message):
        self.message = message
        self.code = code

    def dump(self):
        return self.__dict__


class FieldError(Error):
    def __init__(self, message, field_name, mismatch=False):
        Error.__init__(self, 400, message)
        self.field_name = field_name
        self.mismatch = mismatch


class FatalError(Error):
    def __init__(self, message):
        Error.__init__(self, 500, message)



GENERIC_FATAL_ERROR = FatalError(message="Ups the server made a hiccup")