from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, **kwargs):
        super().__init__()

        if 'id' not in kwargs:
            raise Exception('User must be initialised with key id')

        for arg in kwargs:
            setattr(self, arg, kwargs[arg])


    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)