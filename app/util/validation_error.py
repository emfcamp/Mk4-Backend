class ValidationError:
    def __init__(self, name, message):
        self.name = name
        self.message = message

    def __str__(self):
        return 'Validation Error for %s: %s' % (self.name, self.message)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return (self.name == other.name) and (self.message == other.message)
        return False

    def __repr__(self):
        return 'ValidationError{name: %s,  message: %s}' % (self.name, self.message)
