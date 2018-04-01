class ValidationError(Exception):
    def __init__(self, name, message):
        super(ValidationError, self).__init__('Validation Error for %s: %s' % (name, message))
