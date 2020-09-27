import sys
from tinydb import TinyDB, Query
from docopt import docopt


def main():
    if sys.version_info < (3, 0):
        print('Please make sure you are using Python 3.')
        return

    # initialize the database
    db = TinyDB('db.json')

    users = db.table('users')
    User = Query()

    objects = db.table('objects')
    Object = Query()

    accesses = db.table('access')
    Access = Query()

    cmds_passed = len(sys.argv)

    if len(sys.argv) < 2:
        print('Error: invalid command')
        return

    base_cmd = sys.argv[1].lower()

    if base_cmd == 'adduser':
        if cmds_passed != 4:
            print('Error: invalid number of arguments passed')
            return
        username = sys.argv[2]
        password = sys.argv[3]
        if users.get(User.username == username):
            print ('Error: user exists')
            return
        if username == '':
            print('Error: username missing')
            return
        users.insert({'username': username, 'password': password, 'domains': []})
        print('Success')
        return

    if base_cmd == 'authenticate':
        if cmds_passed != 4:
            print('Error: invalid number of arguments passed')
            return
        username = sys.argv[2]
        password = sys.argv[3]
        user = users.get(User.username == username)
        if not user:
            print('Error: no such user')
            return
        if user['password'] != password:
            print('Error: bad password')
            return
        print('Success')
        return

    if base_cmd == 'setdomain':
        if cmds_passed != 4:
            print('Error: invalid number of arguments passed')
            return
        username = sys.argv[2]
        domain = sys.argv[3]

        # check that user exists
        user = users.get(User.username == username)
        if not user:
            print('Error: no such user')
            return

        if domain == '':
            print('Error: missing domain')
            return

        # add the domain to the user if it doesn't already exist
        if domain not in user['domains']:
            users.update({'domains': user['domains'] + [domain]}, User.username == username)

        print('Success')
        return

    if base_cmd == 'domaininfo':
        if cmds_passed != 3:
            print('Error: invalid number of arguments passed')
            return
        domain = sys.argv[2]
        if domain == '':
            print('Error: missing domain')
            return
        domain_users = users.search(User.domains.any(domain))
        for du in domain_users:
            print(du['username'])

        return

    if base_cmd == 'settype':
        if cmds_passed != 4:
            print('Error: invalid number of arguments passed')
            return
        object_name = sys.argv[2]
        type_name = sys.argv[3]

        if object_name == '':
            print('Error: missing object')
            return
        if type_name == '':
            print('Error: missing type')
            return

        # check if object exists
        object = objects.get(Object.name == object_name)
        if object and type_name not in object['types']:
            objects.update({'types': object['types'] + [type_name]})
        else:
            objects.insert({'name': object_name, 'types': [type_name]})

        print('Success')
        return

    if base_cmd == 'typeinfo':
        if cmds_passed != 3:
            print('Error: invalid number of arguments passed')
            return
        type_name = sys.argv[2]
        if type_name == '':
            print('Error: missing type')
            return
        type_objects = objects.search(Object.types.any(type_name))
        for to in type_objects:
            print(to['name'])

        return

    if base_cmd == 'addaccess':
        if cmds_passed != 5:
            print('Error: invalid number of arguments passed')
            return

        operation = sys.argv[2]
        domain_name = sys.argv[3]
        type_name = sys.argv[4]

        if operation == '':
            print('Error: missing operation')
            return
        if domain_name == '':
            print('Error: missing domain')
            return
        if type_name == '':
            print('Error: missing type')
            return

        access = accesses.get((Access.operation == operation) & (Access.domain == domain_name) & (Access.type == type_name))
        if not access:
            accesses.insert({'operation': operation, 'domain': domain_name, 'type': type_name})

        print('Success')
        return

    if base_cmd == 'canaccess':
        if cmds_passed != 5:
            print('Error: invalid number of arguments passed')
            return

        operation = sys.argv[2]
        username = sys.argv[3]
        object_name = sys.argv[4]

        if operation == '':
            print('Error: missing operation')
            return
        if username == '':
            print('Error: missing user')
            return
        if object_name == '':
            print('Error: missing object')
            return

        # query the user
        user = users.get(User.username == username)
        if not user:
            print('Error: user not found')
            return

        # query the object
        object = objects.get(Object.name == object_name)
        if not object:
            print('Error: object not found')
            return

        for domain in user['domains']:
            for type in object['types']:
                if accesses.get((Access.operation == operation) & (Access.domain == domain) & (Access.type == type)):
                    print('Success')
                    return

        print('Error: access denied')
        return

    if base_cmd == 'reset':
        db.drop_tables()
        print('Success: cleared database.')


if __name__ == '__main__':
    main()
