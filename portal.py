import sys
from tinydb import TinyDB, Query


class Portal:
    CMD_INFO = """Usage:
        portal AddUser <user> <password>
        portal Authenticate <user> <password>
        portal SetDomain <user> <domain>
        portal DomainInfo <domain>
        portal SetType <object> <type>
        portal TypeInfo <type>
        portal AddAccess <operation> <domain> <type>
        portal CanAccess <operation> <user> <object>
        portal Reset
        portal Help
        """

    def __init__(self, db):
        self.db = db

        self.users = self.db.table('users')
        self.User = Query()

        self.objects = self.db.table('objects')
        self.Object = Query()

        self.accesses = self.db.table('access')
        self.Access = Query()

    def add_user(self, username, password):
        if self.users.get(self.User.username == username):
            return 'Error: user exists'
        if username == '':
            return 'Error: username missing'

        self.users.insert({'username': username, 'password': password, 'domains': []})
        return 'Success'

    def authenticate(self, username, password):
        user = self.users.get(self.User.username == username)
        if not user:
            return 'Error: no such user'
        if user['password'] != password:
            return 'Error: bad password'
        return 'Success'

    def set_domain(self, username, domain):
        # check that user exists
        user = self.users.get(self.User.username == username)
        if not user:
            return 'Error: no such user'

        if domain == '':
            return 'Error: missing domain'

        # add the domain to the user if it doesn't already exist
        if domain not in user['domains']:
            self.users.update({'domains': user['domains'] + [domain]}, self.User.username == username)

        return 'Success'

    def domain_info(self, domain):
        if domain == '':
            return 'Error: missing domain'

        domain_users = self.users.search(self.User.domains.any(domain))
        return '\n'.join([domain_user['username'] for domain_user in domain_users])

    def set_type(self, object_name, type_name):
        if object_name == '':
            return 'Error: missing object'

        if type_name == '':
            return 'Error: missing type'

        # check if object exists
        object = self.objects.get(self.Object.name == object_name)
        if object and type_name not in object['types']:
            self.objects.update({'types': object['types'] + [type_name]})
        else:
            self.objects.insert({'name': object_name, 'types': [type_name]})

        return 'Success'

    def type_info(self, type_name):
        if type_name == '':
            return 'Error: missing type'

        type_objects = self.objects.search(self.Object.types.any(type_name))
        return '\n'.join([type_object['name'] for type_object in type_objects])

    def add_access(self, operation, domain_name, type_name):
        if operation == '':
            return 'Error: missing operation'

        if domain_name == '':
            return 'Error: missing domain'

        if type_name == '':
            return 'Error: missing type'

        access = self.accesses.get(
            (self.Access.operation == operation) & (self.Access.domain == domain_name) & (
                    self.Access.type == type_name))
        if not access:
            self.accesses.insert({'operation': operation, 'domain': domain_name, 'type': type_name})

        return 'Success'

    def can_access(self, operation, username, object_name):
        if operation == '':
            return 'Error: missing operation'

        if username == '':
            return 'Error: missing domain'

        if object_name == '':
            return 'Error: missing object'

        # query the user
        user = self.users.get(self.User.username == username)
        if not user:
            return 'Error: user not found'

        # query the object
        object = self.objects.get(self.Object.name == object_name)
        if not object:
            return 'Error: object not found'

        for domain in user['domains']:
            for type in object['types']:
                if self.accesses.get(
                        (self.Access.operation == operation) & (self.Access.domain == domain) & (
                                self.Access.type == type)):
                    return 'Success'

        return 'Error: access denied'

    def reset(self):
        self.db.drop_tables()
        return 'Success: cleared database'

    def execute(self, args):
        args_passed = len(args)

        if args_passed < 2:
            return Portal.CMD_INFO

        base_cmd = args[1].lower()

        if base_cmd == 'adduser':
            if args_passed != 4:
                return 'Usage: portal AddUser <user> <password>'

            return self.add_user(args[2], args[3])

        if base_cmd == 'authenticate':
            if args_passed != 4:
                return 'Usage: portal Authenticate <user> <password>'

            return self.authenticate(args[2], args[3])

        if base_cmd == 'setdomain':
            if args_passed != 4:
                return 'Usage: portal SetDomain <user> <domain>'

            return self.set_domain(args[2], args[3])

        if base_cmd == 'domaininfo':
            if args_passed != 3:
                return 'Usage: portal DomainInfo <domain>'

            return self.domain_info(args[2])

        if base_cmd == 'settype':
            if args_passed != 4:
                return 'Usage: portal SetType <object> <type>'

            return self.set_type(args[2], args[3])

        if base_cmd == 'typeinfo':
            if args_passed != 3:
                return 'Usage: portal TypeInfo <type>'

            return self.type_info(args[2])

        if base_cmd == 'addaccess':
            if args_passed != 5:
                return 'Usage: AddAccess <operation> <domain> <type>'

            return self.add_access(args[2], args[3], args[4])

        if base_cmd == 'canaccess':
            if args_passed != 5:
                return 'Usage: CanAccess <operation> <user> <object>'

            return self.can_access(args[2], args[3], args[4])

        if base_cmd == 'reset':
            return self.reset()

        if base_cmd == 'help':
            return Portal.CMD_INFO

        # an invalid command was entered
        return Portal.CMD_INFO


def main():  # pragma: no cover
    if sys.version_info < (3, 0):
        print('Please make sure you are using Python 3.')
        return
    portal = Portal(TinyDB('db.json'))
    print(portal.execute(sys.argv))


if __name__ == '__main__':  # pragma: no cover
    main()
