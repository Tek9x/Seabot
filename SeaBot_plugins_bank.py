import json

with open('data/users.json') as f:
    db = json.load(f)


class Bank(object):
    def __init__(self, account_name, account_balance):
        self.account_name = account_name
        self.account_balance = account_balance
        self.db = db
        self.accounts = db['accounts']

    def check(self, uname):
        if uname in self.db['accounts']:
            return True
        else:
            return False

    def openaccount(self):
        self.accounts[self.account_name] = self.account_balance

    def saveaccount(self):
        data = self.db
        with open('data/users.json', 'w') as outfile:
            json.dump(data, outfile)

    def deleteaccount(self):
        del self.accounts[self.account_name]
