import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

import script

from errbot import BotPlugin, re_botcmd, botcmd, arg_botcmd, webhook
from time import sleep

class Digit(BotPlugin):
    """
    A set of dialogs for SuperTech Awards
    """

    dialog = script.script["digit"]

    def callback_message(self, message):
        """
        Triggered for every received message that isn't coming from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        self.log.debug("> %s", message)
        self.log.debug("dict > %s", self.dialog)
        for callword in self.dialog:
            self.log.debug("callword > %s", callword)
            if message.body.find(callword) != -1:
                reply = self.dialog[callword]
                self.log.debug("found callword > %s reply %s after %s ms",
                               callword,
                               reply[1],
                               reply[0])
                sleep(reply[0])
                self.send(
                    message.frm,
                    reply[1]
                    )
