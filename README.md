# access-control
Project 1 for CS419 Computer Security at Rutgers University

## Local Setup

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