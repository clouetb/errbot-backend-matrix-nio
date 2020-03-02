import logging
import sys

from errbot.backends.base import RoomError, Identifier, Person, RoomOccupant, Stream, ONLINE, Room, Message, Backend
from errbot.core import ErrBot
from errbot.rendering.ansiext import enable_format, TEXT_CHRS

from urllib.parse import quote

# Can't use __name__ because of Yapsy.
log = logging.getLogger('errbot.backends.matrix-nio')

try:
    import asyncio
    import nio
except ImportError:
    log.exception("Could not start the Matrix Nio back-end")
    log.fatal(
        "You need to install the Matrix Nio support in order "
        "to use the Matrix Nio backend.\n"
        "You should be able to install this package using:\n"
        "pip install matrix-nio"
    )
    sys.exit(1)


class MatrixNioRoomError(RoomError):
    def __init__(self, message=None):
        if message is None:
            message = (
                "I currently do not support this request :(\n"
                "I still love you."
            )
        super().__init__(message)


class MatrixNioIdentifier(Identifier):
    def __init__(self, id):
        self._id = str(id)

    @property
    def id(self):
        return self._id

    def __unicode__(self):
        return str(self._id)

    def __eq__(self, other):
        return self._id == other.id

    __str__ = __unicode__


# `MatrixNioPerson` is used for both 1-1 PMs and Group PMs.
class MatrixNioPerson(MatrixNioIdentifier, Person):
    def __init__(self, id, full_name, emails, client: nio.AsyncClient = None):
        super().__init__(id)
        self._full_name = full_name
        self._emails = emails
        self._client = client

    @property
    def person(self):
        """
        Maps to user_id
        :return: user_id
        """
        return self._id

    @property
    def fullname(self):
        """
        Maps to ProfileGetResponse.displayname
        :return: ProfileGetResponse.displayname
        """
        return self._full_name

    @property
    def nick(self):
        """
        Maps to ProfileGetResponse.displayname
        :return: ProfileGetResponse.displayname
        """
        return self._full_name

    @property
    def client(self):
        """
        Maps to AsyncClient
        :return: AsyncClient
        """
        return self._client

    @property
    def emails(self):
        """
        Maps to ProfileGetResponse.other_info['address']
        :return: ProfileGetResponse.other_info['address']
        """
        return self._emails

    @property
    def aclattr(self):
        """
        Maps to ProfileGetResponse.other_info['address']
        :return: ProfileGetResponse.other_info['address']
        """
        return ','.join(sorted(self._emails))


# `MatrixNioRoom` is used for messages to streams.
class MatrixNioRoom(MatrixNioIdentifier, Room):
    def __init__(self, title, id=None, subject=None, client: nio.AsyncClient = None):
        super().__init__(id)
        self._title = title
        self._subject = subject
        self._client = client
        self.matrix_room = self._client.rooms[id]

    @property
    def id(self):
        """
        Maps to MatrixRoom.room_id
        :return: MatrixRoom.room_id
        """
        return self._id

    @property
    def aclattr(self):
        """
        Maps to MatrixRoom.own_user_id
        :return: MatrixRoom.own_user_id
        """
        return self.matrix_room.own_user_id

    @property
    def subject(self):
        """
        Maps to MatrixRoom.topic
        :return: MatrixRoom.topic
        """
        return self.matrix_room.topic

    @property
    def title(self):
        """
        Maps to MatrixRoom.display_name
        :return: MatrixRoom.display_name
        """
        return self.matrix_room.display_name

    @property
    def exists(self) -> bool:
        pass

    @property
    def joined(self) -> bool:
        pass

    def destroy(self) -> None:
        pass

    def join(self, username: str = None, password: str = None):
        result = await self._client.join(self.id)
        if isinstance(result, nio.JoinError):
            raise MatrixNioRoomError(result)

    def create(self):
        result = await self._client.room_create(
            name=self.title,
            topic=self.subject
        )
        if isinstance(result, nio.RoomCreateError):
            raise MatrixNioRoomError(result)

    def leave(self, reason: str=None):
        result = await self._client.room_leave(self.id)
        if isinstance(result, nio.RoomLeaveError):
            raise MatrixNioRoomError(result)

    @property
    def topic(self):
        """
        Maps to MatrixRoom.topic
        :return: MatrixRoom.topic
        """
        return self.matrix_room.topic

    @property
    def occupants(self):
        """
        Maps to MatrixRoom.users
        :return: MatrixRoom.users
        """
        users = self.matrix_room.users
        occupants = []
        for i in users:
            an_occupant = MatrixNioRoomOccupant(id=i.user_id, full_name=i.display_name, client=self._client)
            occupants.append(an_occupant)
        return occupants

    def invite(self, *args):
        for i in args:
            result = self._client.room_invite(i.user_id)


class MatrixNioRoomOccupant(MatrixNioPerson, RoomOccupant):
    """
    This class represents a person subscribed to a stream.
    """
    def __init__(self, id, full_name, emails, client, room):
        super().__init__(id=id, full_name=full_name, emails=emails, client=client)
        self._room = room

    @property
    def room(self):
        return self._room


class MatrixNioBackend(Backend):
    def __init__(self, config):
        super().__init__(config)

        self.identity = config.BOT_IDENTITY
        for key in ('email', 'auth_dict', 'site'):
            if key not in self.identity:
                log.fatal(
                    "You need to supply the key `{}` for me to use. `{key}` and its value "
                    "can be found in your bot's `matrixniorc` config file.".format(key)
                )
                sys.exit(1)

        self.client = nio.AsyncClient(
            self.identity['site'],
            self.identity['email']
        )
        self.client.add_event_callback(self._handle_message, nio.RoomMessageText)
        log.info("Initializing connection")
        await self.client.login_raw(self.identity['auth_dict'])
        assert self.client.client_session
        log.info("Connected")

    def serve_once(self):
        self.bot_identifier = self.build_identifier(self.client.user)
        try:
            self.reset_reconnection_count()
            self.connect_callback()
        except KeyboardInterrupt:
            log.info("Interrupt received, shutting down..")
            await self.client.logout()
            return True  # True means shutdown was requested.
        except Exception:
            log.exception("Error reading from Matrix Nio updates rooms.")
            raise
        finally:
            return

    def _handle_message(self, room: nio.MatrixRoom, event: nio.Event):
        """
        Handles incoming messages.
        In Zulip, there are three types of messages: Private messages, Private group messages,
        and Stream messages. This plugin handles Group PMs as normal PMs between the bot and the
        user. Stream messages are handled as messages to rooms.
        """
        if not isinstance(event, nio.RoomMessageText):
            log.warning("Unhandled message type (not a text message) ignored")
            return

        message_instance = self.build_message(event.body)
        message_instance.frm = MatrixNioRoomOccupant(
            id=event.sender,
            full_name=room.user_name(event.sender),
            emails=[event.sender],
            client=self.client,
            room=room.room_id
        )
        room_instance = MatrixNioRoom(
            id=room.room_id,
            title=room.name,
            subject=room.display_name,
            client=self.client
        )
        message_instance.to = room_instance
        self.callback_message(message_instance)

    log.debug("Triggering disconnect callback.")

    def send_message(self, msg: Message):
        super().send_message(msg)
        msg_data = {
            'msgtype': "m.text",
            'body': msg.body
        }
        try:
            await self.client.send(
                room_id=msg.to,
                message_type='m.room.message',
                content=msg_data
            )
        except Exception:
            log.exception(
                "An exception occurred while trying to send the following message "
                "to %s: %s" % (msg.to.id, msg.body)
            )
            raise

    def connect_callback(self) -> None:
        pass

    def disconnect_callback(self) -> None:
        pass

    def is_from_self(self, msg: Message):
        return msg.frm.aclattr == self.client.user_id

    def change_presence(self, status: str = ONLINE, message: str = '') -> None:
        # At this time, this backend doesn't support presence
        pass

    def build_identifier(self, txtrep):
        profile = self.client.get_profile(txtrep)
        return MatrixNioPerson(id=txtrep,
                               full_name=profile.displayname,
                               emails=[txtrep],
                               client=self.client)

    def build_reply(self, msg, text=None, private=False, threaded=False):
        response = self.build_message(text)
        response.to = msg.to
        return response

    @property
    def mode(self):
        return 'matrix-nio'

    def query_room(self, room):
        return MatrixNioRoom(title=room, client=self.client)

    def rooms(self):
        result = await self.client.joined_rooms()
        return [MatrixNioRoom(title=subscription, id=subscription) for subscription in result]

    def prefix_groupchat_reply(self, message, identifier):
        super().prefix_groupchat_reply(message, identifier)
        message.body = '@{0} {1}'.format(identifier.full_name, message.body)
