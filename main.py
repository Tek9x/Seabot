import time
import json
import requests

import Skype4Py
import plugins.bank
import plugins.slotmachine

with open('data/users.json') as f:
    db = json.load(f)

with open('data/pkm.json') as f:
    pk = json.load(f)


class SeaBot(object):
    def __init__(self):
        self.skype = Skype4Py.Skype()
        if self.skype.Client.IsRunning == False:
            self.skype.Client.Start()
        try:
            self.skype.OnAttachmentStatus = self.OnAttach
            self.skype.Attach()
            self.skype.OnMessageStatus = self.RunFunction
        except AssertionError:
            raise Skype4Py.SkypeAPIError('Unable to Attach')

        self.context = ''
        self.db = db
        self.accounts = db['accounts']
        self.key = 'dc6zaTOxFJmzC'


    def AttachmentStatusText(self, status):
        return self.skype.Convert.AttachmentStatusToText(status)

    def OnAttach(self, status):
        print 'API attachment status: ' + self.AttachmentStatusText(status)
        if status == Skype4Py.apiAttachAvailable:
            self.skype.Attach()

    def RunFunction(self, Message, Status):
        if Status == 'SENT' or Status == 'RECEIVED':
            bot = Message.Body.split(' ')[0]
            main = Message.Body.split(' ')[1]
            cmd = Message.Body.split(' ')[2]
            if bot == '//seabot' and main == 'bank' and cmd in self.bankc.keys():
                self.context = Message
                self.bankc[cmd](self)
            elif bot == '//seabot' and main == 'slot_machine' and cmd in self.casino.keys():
                self.context = Message
                self.casino[cmd](self)
            elif bot == '//seabot' and main == 'pokemon' and cmd in self.pok.keys():
                self.context = Message
                self.pok[cmd](self)
            elif bot == '//seabot' and main == 'imagetools' and cmd in self.imagetools.keys():
                self.context = Message
                self.imagetools[cmd](self)
            elif bot == '//seabot' and main == 'tools' and cmd in self.misc.keys():
                self.context = Message
                self.misc[cmd](self)

                # --------------Bank Plugin Start-------------------------------------#

    def create(self):
        new = plugins.bank.Bank(self.context.FromHandle, 100)
        if not new.check(self.context.FromHandle):
            new.openaccount()
            new.saveaccount()
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: User: ['
                                          + self.context.FromHandle
                                          + '] Thank you for choosing us as your bank , please accept 100 rubles for creating a new account with us today!'
            )
        else:
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: User: ['
                                          + self.context.FromHandle
                                          + '] i see you already have an account with us')

    def delete(self):
        rub = plugins.bank.Bank(self.context.FromHandle, 0)
        try:
            rub.deleteaccount()
            rub.saveaccount()
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: User: '
                                          + self.context.FromHandle
                                          + ' [Account Status]: Suspended')
        except KeyError:
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: User: '
                                          + self.context.FromHandle
                                          + ' [Account Status]: Not Found')

    def balance(self):
        try:
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: User: '
                                          + self.context.FromHandle + ' [Balance]: '
                                          + str(self.accounts[self.context.FromHandle]) + 'rB'
            )
        except KeyError:
            self.context.Chat.SendMessage(
                '/me [The Kondor Treasury]: We could not find that account on file or you do not have an account with us yet.')

    def payto(self):
        try:
            r = self.context.Body.split(' ')[3]
        except IndexError:
            self.context.Chat.SendMessage('/me [CamelBot]: Please use proper syntax !pay [Account] [Money]'
            )
            return
        try:
            a = self.context.Body.split(' ')[4]
        except IndexError:
            self.context.Chat.SendMessage('/me [CamelBot]: Please use proper syntax !pay [Account] [Money]'
            )
            return
        checkon = plugins.bank.Bank(' ', 0)
        if not checkon.check(r):
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: We could not find that account on file.'
            )
        elif int(a) < 0:
            self.context.Chat.SendMessage(
                '/me [The Kondor Treasury]: Invalid Numbers, please use postive intergers only.'
            )
        elif int(a) > self.accounts[self.context.FromHandle]:
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: User: '
                                          + self.context.FromHandle
                                          + ' you have\n [Status] Insufficient Funds for this transfer'
            )
        else:
            rub = plugins.bank.Bank(self.context.FromHandle, 0)
            self.accounts[self.context.FromHandle] -= int(a)
            self.accounts[r] += str(a)
            self.context.Chat.SendMessage('/me [The Kondor Treasury]: User: '
                                          + self.context.FromHandle + ' wrote a check to '
                                          + r + ' for [Money]: ' + a + 'rB')
            rub.saveaccount()

    def listacc(self):
        accounts = []
        for i in self.accounts:
            accounts.append(i)
        self.context.Chat.SendMessage('/me [The Kondor Treasury]: Found ' + str(len(accounts)) + ' accounts on file ' + '[Accounts]: ' + str(accounts))


            # --------------Bank Plugin End-------------------------------------#

        # ------------slot machine plugin start--------------------------------#

    def slot_machine(self):
        firstWheel = plugins.slotmachine.spin_wheel()
        secondWheel = plugins.slotmachine.spin_wheel()
        thirdWheel = plugins.slotmachine.spin_wheel()

        if ((firstWheel == "Cherry") and (secondWheel != "Cherry")):
            win = 2
        elif ((firstWheel == "Cherry") and (secondWheel == "Cherry") and (thirdWheel != "Cherry")):
            win = 5
        elif ((firstWheel == "Cherry") and (secondWheel == "Cherry") and (thirdWheel == "Cherry")):
            win = 7
        elif ((firstWheel == "Orange") and (secondWheel == "Orange") and (
                    (thirdWheel == "Orange") or (thirdWheel == "Bar"))):
            win = 10
        elif ((firstWheel == "Plum") and (secondWheel == "Plum") and ((thirdWheel == "Plum") or (thirdWheel == "Bar"))):
            win = 14
        elif ((firstWheel == "Bell") and (secondWheel == "Bell") and ((thirdWheel == "Bell") or (thirdWheel == "Bar"))):
            win = 20
        elif ((firstWheel == "Bar") and (secondWheel == "Bar") and (thirdWheel == "Bar")):
            win = 250
        else:
            win = -1

        if win > 0:
            self.context.Chat.SendMessage(
                "/me [Royal Slots]: o-{" + firstWheel + "-" + secondWheel + "-" + thirdWheel + "}-o" + ' ' + "[User]: " + self.context.FromHandle + " [Result]: win " + "[Payout]: " + str(
                    win) + 'rB')
        else:
            self.context.Chat.SendMessage(
                "/me [Royal Slots]: o-{" + firstWheel + "-" + secondWheel + "-" + thirdWheel + "}-o" + ' ' + '[User]: ' + self.context.FromHandle + ' [Result]: lose')
        # ----------slot machine plugin end-----------------#

        #----Pokedex Plugin start------#

    def find_pokemon(self):
        pkm_id = self.context.Body.split(' ')[3]
        try:
            print 'doing routine'
            result = filter(lambda pokemon: pokemon['name'] == pkm_id.capitalize(), pk)
            self.context.Chat.SendMessage("/me Name: {0}".format(result[0]['name']))
            print SeaBot.dumpclean(self, "/me Type: ", result[0]['type'])
            self.context.Chat.SendMessage("/me Height: {0}".format(result[0]['height']))
            self.context.Chat.SendMessage("/me Weight: {0}".format(result[0]['weight']))
            print SeaBot.dumpclean(self, "/me Ability: ", result[0]['abilities'])
            print SeaBot.dumpclean(self, "/me Weakness: ", result[0]['weakness'])
            self.context.Chat.SendMessage("/me Pokedex: #{0}".format(result[0]['id']))
            self.context.Chat.SendMessage("/me Picture: {0}".format(result[0]['ThumbnailImage']))
            self.context.Chat.SendMessage(
                "/me More Details: http://www.pokemon.com{0}".format(result[0]['detailPageURL']))
        except IndexError:
            print "Invaild Pokemon"

    def dumpclean(self, name, obj):
        if type(obj) == dict:
            for k, v in obj.items():
                if hasattr(v, '__inter__'):
                    print k
                    dumpclean(v)
                else:
                    print '%s : %s' % (k, v)
        elif type(obj) == list:
            for v in obj:
                if hasattr(v, '__inter__'):
                    dumpclean(v)
                else:
                    self.context.Chat.SendMessage(name + v)
        else:
            print obj
        # ----------------End Plugin------@

    def text2gif(self):
        search = self.context.Body.split(' ')[3]
        r = requests.get('http://api.giphy.com/v1/gifs/translate?s='
                         + search + '&api_key=' + self.key + '&limit=1')
        info = r.json()
        try:
            url = info['data']['url']
        except TypeError:
            self.context.Chat.SendMessage(
                '/me Too Complicated of a Gif Search i am in Alpha Stage , please try a more simple word!'
            )
            return
        self.context.Chat.SendMessage('/me [Seabot]: gif translation for '
                                      + search + ' is ' + url)
         # ----------------End Plugin------@

    def weather(self):
        print 'Dubug: doing it'
        search = self.context.Body.split(' ')[3]
        r = requests.get('http://5DayWeather.org/api.php?city=' + search)
        info = r.json()
        loc = info['data']['location']
        day = info['data']['day']
        date = info['data']['date']
        sky = info['data']['skytext']
        temp = info['data']['temperature']
        hum = info['data']['humidity']
        wind = info['data']['wind']
        self.context.Chat.SendMessage('/me On ' + day + ' the ' + date[8:10] + 'th' + ' in beautiful ' + loc + ' it is ' + sky + ' with a temperature of ' + temp + ' degrees and humidity at ' + hum + " with a nice cool wind breeze at " + wind + ' mph')




    bankc = {
        'open_account': create,
        'delete_account': delete,
        'check_balance': balance,
        'payto_account': payto,
        'list_accounts': listacc}

    casino = {'pull_lever': slot_machine}

    pok = {'dex': find_pokemon}

    imagetools = {'gif_translate': text2gif}

    misc = {'weather_get': weather}


if __name__ == '__main__':
    Start = SeaBot()
    while True:
        time.sleep(1)

