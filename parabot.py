# Parabot.py
# Written by Yousef Amar Christmas '11
# Uses IRCBot by Joel Rosdahl <joel@rosdahl.net>
# and A.L.I.C.E. AIML files

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, irc_lower, ip_numstr_to_quad
import string, aiml, os, time

class ParaBrain():
    
    k = aiml.Kernel()
    
    def __init__(self, bot):
        self.k.learn("std-startup.xml")
        dirList=os.listdir(os.getcwd()+"/aiml")
        for fname in dirList:
            if fname.startswith("reduction"):
                self.k.learn("aiml/"+fname)
        for fname in dirList:
            if fname.startswith("mp"):
                self.k.learn("aiml/"+fname)
        for fname in dirList:
            if not fname.startswith("reduction") and not fname.startswith("mp"):
                self.k.learn("aiml/"+fname)
        with open("botprops.properties") as f:
            for line in f:
                props = line.split("=")
                self.k.setBotPredicate(props[0].strip(), props[1].strip())
        self.k.respond("load aiml b")
           
    def processData(self, bot, chat, nick, rawText, cleanText):
        cleanText = cleanText.replace(irc_lower(chat.get_nickname()), "").strip()
        time.sleep(0.25*len(cleanText))
        bot.say(chat, self.k.respond(cleanText))

class ParaBot(SingleServerIRCBot):
    brain = None
    
    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.brain = ParaBrain(self)

    def getBossName(self):
        return "paraknight"

    def on_nicknameinuse(self, c, e):
        oldNick = c.get_nickname()
        c.nick(oldNick + oldNick[-1])

    def on_welcome(self, c, e):
        c.join(self.channel)
        
    def say(self, c, text):
        """Sends a public message."""
        # Should limit len(text) here!
        c.privmsg(self.channel, text)

    def on_privmsg(self, c, e):
        nick = nm_to_n(e.source())
        if not nick == self.getBossName():
            c.privmsg(nick, "One does not simply PM me, " + nick + ". Only "+self.getBossName()+" may. I refuse to listen.")
        else:
            self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        rawText = e.arguments()[0]
        cleanText = irc_lower(rawText).translate(string.maketrans("",""), string.punctuation)
        sourceNick = nm_to_n(e.source())
        botNick = irc_lower(c.get_nickname())
        if sourceNick == self.getBossName() and irc_lower(rawText).startswith(botNick+"!"):
            self.do_command(e, cleanText.split()[1])
        elif cleanText.startswith(botNick+" ") or cleanText.endswith(" "+botNick) or not cleanText.find(" "+botNick+" ") is -1 or cleanText == botNick:
            self.brain.processData(self, c, sourceNick, rawText, cleanText)

    def on_dccchat(self, c, e):
        if len(e.arguments()) != 2:
            return
        args = e.arguments()[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        else:
            self.connection.notice(nm_to_n(e.source()), "I don't how to " + cmd)

def main():
    bot = ParaBot("#reddit-gamedev", "Nova", "irc.freenode.net", 6667)
    bot.start()

if __name__ == "__main__":
    main()
