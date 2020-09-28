import unittest
from portal import Portal
from tinydb import TinyDB
import warnings


class TestPortal(unittest.TestCase):

    def setUp(self):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        self.portal = Portal(TinyDB('test_db.json'))
        self.portal.reset()

    def test_add_user(self):
        self.assertEqual(self.portal.add_user('bob', 'password123'), 'Success')
        added_user = self.portal.users.get(self.portal.User.username == 'bob')
        self.assertTrue(added_user, 'A user with username "bob" should exists.')
        self.assertEqual(added_user['username'], 'bob', 'The user\'s username should be "bob".')
        self.assertEqual(added_user['password'], 'password123', 'The user\'s password should be "password123')
        self.assertEqual(len(added_user['domains']), 0, "The user's domains should be an empty array.")

        self.assertEqual(self.portal.add_user('bob', 'password123'), 'Error: user exists', 'Should return an error if the a user already exists.')

        self.assertEqual(self.portal.add_user('', 'password123'), 'Error: username missing', 'Should return an error if the username is missing')

    def test_authenticate(self):
        self.portal.add_user('bob', 'password123')
        self.assertEqual(self.portal.authenticate('bob', 'password123'), 'Success', 'Given the correct username and password, should return "Success".')
        self.assertEqual(self.portal.authenticate('bob', 'wrongpassword'), 'Error: bad password', 'Given the incorrect password should return "Error: bad password"')
        self.assertEqual(self.portal.authenticate('alice', 'password123'), 'Error: no such user', 'Given a user that does not exist, should return "Error: no such user".')

    def test_set_domain(self):
        self.portal.add_user('bob', 'password123')
        self.portal.set_domain('bob', 'student')
        added_user = self.portal.users.get(self.portal.User.username == 'bob')
        self.assertTrue(added_user, 'A user with username "bob" should exists.')
        self.assertIn('student', added_user['domains'], 'Bob should belong in the "student" domain.')

        self.assertEqual(self.portal.set_domain('alice', 'student'), 'Error: no such user')

        self.assertEqual(self.portal.set_domain('bob', ''), 'Error: missing domain')

    def test_domain_information(self):
        self.portal.add_user('bob', 'password123')
        self.portal.add_user('alice', 'password123')
        self.portal.add_user('james', 'password123')
        self.portal.set_domain('bob', 'student')
        self.portal.set_domain('alice', 'student')
        self.portal.set_domain('james', 'student')
        self.assertEqual(self.portal.domain_info('student'), 'bob\nalice\njames', 'Should return bob, alice, and james as being in the student domain.')

        self.assertEqual(self.portal.domain_info(''), 'Error: missing domain', 'Should return an error if domain is empty.')

    def test_set_type(self):
        self.assertEqual(self.portal.set_type('chrome', 'application'), 'Success')
        created_object = self.portal.objects.get(self.portal.Object.name == 'chrome')
        self.assertTrue(created_object, "Object should have been created.")
        self.assertEqual(created_object['name'], 'chrome', 'Object name should be chrome.')
        self.assertIn('application', created_object['types'], 'Object should be associated with type application.')

        self.assertEqual(self.portal.set_type('', 'application'), 'Error: missing object', 'Should return error if object is empty.')
        self.assertEqual(self.portal.set_type('chrome', ''), 'Error: missing type', 'Should return error if type is empty.')

    def test_type_info(self):
        self.portal.set_type('chrome', 'application')
        self.portal.set_type('firefox', 'application')
        self.portal.set_type('edge', 'application')
        self.portal.set_type('safari', 'application')

        self.portal.set_type('resume.txt', 'document')
        self.portal.set_type('essay.txt', 'document')

        self.assertEqual(self.portal.type_info('application'), 'chrome\nfirefox\nedge\nsafari', 'Should return chrome, firefox, edge, and safari as in the domain "application".')
        self.assertEqual(self.portal.type_info('document'), 'resume.txt\nessay.txt', 'Should return resume.txt and essay.txt as in the domain "document".')
        self.assertEqual(self.portal.type_info('config'), '', 'Should return nothing in the domain "config".')

        self.assertEqual(self.portal.type_info(''), 'Error: missing type', 'Should return error if type is empty.')

    def test_add_access(self):
        self.assertEqual(self.portal.add_access('write', 'student', 'document'), 'Success')
        created_access = self.portal.accesses.get(self.portal.Access.operation == 'write')
        self.assertTrue(created_access, 'A new access entry should have been created.')

        self.assertEqual(created_access['operation'], 'write', 'The operation field should be "write".')
        self.assertEqual(created_access['domain'], 'student', 'The domain field should be "student".')
        self.assertEqual(created_access['type'], 'document', 'The type field should be "document".')

        self.assertEqual(self.portal.add_access('', 'student', 'document'), 'Error: missing operation', "Should throw an error if operation is empty.")
        self.assertEqual(self.portal.add_access('write', '', 'document'), 'Error: missing domain', "Should throw an error if domain is empty.")
        self.assertEqual(self.portal.add_access('write', 'student', ''), 'Error: missing type', "Should throw an error if type is empty.")

    def test_can_access(self):
        self.portal.add_user('bob', 'password123')
        self.portal.add_user('alice', 'password123')
        self.portal.add_user('james', 'password123')

        self.portal.set_domain('bob', 'student')
        self.portal.set_domain('alice', 'employee')
        self.portal.set_domain('james', 'admin')

        self.portal.set_type('essay.txt', 'homework')
        self.portal.set_type('chart.pdf', 'company')
        self.portal.set_type('hosts.txt', 'config')

        self.portal.add_access('write', 'student', 'homework')
        self.portal.add_access('read', 'student', 'homework')
        self.portal.add_access('read', 'student', 'company')

        self.portal.add_access('read', 'employee', 'company')
        self.portal.add_access('write', 'employee', 'company')

        self.portal.add_access('write', 'admin', 'config')
        self.portal.add_access('read', 'admin', 'config')
        self.portal.add_access('write', 'admin', 'homework')
        self.portal.add_access('read', 'admin', 'homework')
        self.portal.add_access('write', 'admin', 'company')
        self.portal.add_access('read', 'admin', 'company')

        self.assertEqual(self.portal.can_access('read', 'bob', 'essay.txt'), 'Success', 'bob should be able to read from essay.txt.')
        self.assertEqual(self.portal.can_access('write', 'bob', 'essay.txt'), 'Success', 'bob should be able to write to essay.txt.')
        self.assertEqual(self.portal.can_access('read', 'bob', 'chart.pdf'), 'Success', 'bob should be able to read from chart.pdf.')
        self.assertEqual(self.portal.can_access('write', 'bob', 'chart.pdf'), 'Error: access denied', 'bob should not be able to write to chart.pdf.')
        self.assertEqual(self.portal.can_access('write', 'bob', 'hosts.txt'), 'Error: access denied', 'bob should not be able to write to hosts.txt.')
        self.assertEqual(self.portal.can_access('read', 'bob', 'hosts.txt'), 'Error: access denied', 'bob should not be able to read from hosts.txt.')

        self.assertEqual(self.portal.can_access('read', 'alice', 'chart.pdf'), 'Success', 'alice should be able to read from chart.pdf.')
        self.assertEqual(self.portal.can_access('write', 'alice', 'chart.pdf'), 'Success', 'alice should be able to write to chart.pdf.')
        self.assertEqual(self.portal.can_access('read', 'alice', 'essay.txt'), 'Error: access denied', 'alice should not be able to read from essay.txt.')
        self.assertEqual(self.portal.can_access('write', 'alice', 'essay.txt'), 'Error: access denied', 'alice should not be able to write to essay.txt.')
        self.assertEqual(self.portal.can_access('read', 'alice', 'hosts.txt'), 'Error: access denied', 'alice should not be able to read from hosts.txt.')
        self.assertEqual(self.portal.can_access('write', 'alice', 'essay.txt'), 'Error: access denied', 'alice should not be able to write to essay.txt.')

        self.assertEqual(self.portal.can_access('read', 'james', 'hosts.txt'), 'Success', 'james should be able to read from hosts.txt.')
        self.assertEqual(self.portal.can_access('write', 'james', 'hosts.txt'), 'Success', 'james should be able to write to hosts.txt.')
        self.assertEqual(self.portal.can_access('read', 'james', 'chart.pdf'), 'Success', 'james should be able to read from chart.pdf.')
        self.assertEqual(self.portal.can_access('write', 'james', 'chart.pdf'), 'Success', 'james should be able to write to chart.pdf.')
        self.assertEqual(self.portal.can_access('read', 'james', 'essay.txt'), 'Success', 'james should be able to read from essay.txt.')
        self.assertEqual(self.portal.can_access('write', 'james', 'essay.txt'), 'Success', 'james should be able to write to essay.txt.')

        self.assertEqual(self.portal.can_access('write', 'fred', 'essay.txt'), 'Error: user not found', 'fred does not exist and should return an error')
        self.assertEqual(self.portal.can_access('write', 'james', 'random.csv'), 'Error: object not found', 'random.csv does not exist and should return an error')

    def test_execution(self):
        # testing invalid commands
        self.assertEqual(self.portal.execute(['portal.py', 'asdf']), self.portal.CMD_INFO)
        self.assertEqual(self.portal.execute(['portal.py']), self.portal.CMD_INFO)

        # run through short scenario
        self.assertEqual(self.portal.execute(['portal.py', 'AddUser', 'bob', 'password']), 'Success')
        self.assertEqual(self.portal.execute(['portal.py', 'AddUser', 'alice', 'password']), 'Success')

        self.assertEqual(self.portal.execute(['portal.py', 'SetDomain', 'bob', 'employee']), 'Success')
        self.assertEqual(self.portal.execute(['portal.py', 'SetDomain', 'alice', 'management']), 'Success')

        self.assertEqual(self.portal.execute(['portal.py', 'DomainInfo', 'employee']), 'bob')
        self.assertEqual(self.portal.execute(['portal.py', 'DomainInfo', 'management']), 'alice')

        self.assertEqual(self.portal.execute(['portal.py', 'SetType', 'word', 'application']), 'Success')
        self.assertEqual(self.portal.execute(['portal.py', 'SetType', 'timesheet', 'hr']), 'Success')

        self.assertEqual(self.portal.execute(['portal.py', 'TypeInfo', 'application']), 'word')
        self.assertEqual(self.portal.execute(['portal.py', 'TypeInfo', 'hr']), 'timesheet')

        self.assertEqual(self.portal.execute(['portal.py', 'AddAccess', 'write', 'employee', 'application']), 'Success')
        self.assertEqual(self.portal.execute(['portal.py', 'AddAccess', 'write', 'management', 'hr']), 'Success')

        self.assertEqual(self.portal.execute(['portal.py', 'CanAccess', 'write', 'bob', 'word']), 'Success')
        self.assertEqual(self.portal.execute(['portal.py', 'CanAccess', 'write', 'bob', 'timesheet']), 'Error: access denied')
        self.assertEqual(self.portal.execute(['portal.py', 'CanAccess', 'write', 'alice', 'timesheet']), 'Success')
        self.assertEqual(self.portal.execute(['portal.py', 'CanAccess', 'write', 'alice', 'word']), 'Error: access denied')

    def tearDown(self):
        self.portal.reset()


if __name__ == '__main__':
    unittest.main()
