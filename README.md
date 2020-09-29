# portal
Project 1 for CS419 Computer Security at Rutgers University.

## Description
This project is a simplified implementation of an access control library. I used [tinydb](https://tinydb.readthedocs.io/en/latest/), a lightweight document based database to handle data persistence. Any persisted data will reside in db.json by default which will be generated if it does not exist. There are three main collections: users, objects, and accesses. Domains and types are denormalized in a list within user and object documents respectively. Access documents represent a mapping between operations, domains, and types. This repository is well tested with 100% code coverage. The source code resides in `portal.py` and tests in `tests.py`.

## Local Setup
1. Clone the repository to a local directory.
2. Make sure you have python 3 available on your system.
3. Install the required dependencies by running `pip install -r requirements.txt` on iLabs run `pip3 install --user -r requirements.txt`. Only tinydb is technically required to run the program, however the coverage package is required to view code coverage.
4. Run the tests using `python -m unit` on iLabs run `python3 -m unit`
5. Generate code coverage by running `coverage run -m unittest tests.py`
6. View the coverage report in the terminal with `coverage report` or in html with `coverage html`

## Usage
On iLabs machines you have to use `python3` instead of `python`.
```shell script
python portal.py AddUser <user> <password>
python portal.py Authenticate <user> <password>
python portal.py SetDomain <user> <domain>
python portal.py DomainInfo <domain>
python portal.py SetType <object> <type>
python portal.py TypeInfo <type>
python portal.py AddAccess <operation> <domain> <type>
python portal.py CanAccess <operation> <user> <object>
python portal.py Reset
python portal.py Help
```
The `Reset` command will clear the database while the `Help` command will show a prompt of the API.
You can alias `python portal.py` to `portal` in bash if you want to make the cli more concise.

## Sample Test Case
```shell script
$ python portal.py AddUser bob password
Success
$ python portal.py AddUser alice password
Success
$ python portal.py SetDomain bob employee
Success
$ python portal.py SetDomain alice management
Success        
$ python portal.py DomainInfo employee
bob
$ python portal.py DomainInfo management
alice
$ python portal.py SetType word application
Success
$ python portal.py SetType timesheet hr
Success
$ python portal.py TypeInfo application
word
$ python portal.py TypeInfo hr
timesheet
$ python portal.py AddAccess write employee application
Success
$ python portal.py AddAccess write management hr
Success
$ python portal.py CanAccess write bob word
Success
$ python portal.py CanAccess write bob timesheet
Error: access denied
$ python portal.py CanAccess write alice timesheet
Success
$ python portal.py CanAccess write alice word
Error: access denied
```
### Resulting db.json
After running the above test cases, `db.json` should look exactly like this.
```json
{
  "users": {
    "1": {
      "username": "bob",
      "password": "password",
      "domains": [
        "employee"
      ]
    },
    "2": {
      "username": "alice",
      "password": "password",
      "domains": [
        "management"
      ]
    }
  },
  "objects": {
    "1": {
      "name": "word",
      "types": [
        "application"
      ]
    },
    "2": {
      "name": "timesheet",
      "types": [
        "hr"
      ]
    }
  },
  "access": {
    "1": {
      "operation": "write",
      "domain": "employee",
      "type": "application"
    },
    "2": {
      "operation": "write",
      "domain": "management",
      "type": "hr"
    }
  }
}
```
