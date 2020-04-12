import logging
import sys
from typing import Any, Coroutine, Optional, List

from errbot.backends.base import RoomError, Identifier, Person, RoomOccupant, Room, Message, ONLINE
from errbot.core import ErrBot
from nio import LoginError, AsyncClientConfig, RoomSendResponse, ErrorResponse, JoinedRoomsError, RoomForgetError

log = logging.getLogger('errbot.backends.matrix-nio')

try:
    import asyncio
    import nio
except ImportError:
    log.exception("Could not start the Matrix Nio back-end")
    log.error(
        "You need to install the Matrix Nio support in order "
        "to use the Matrix Nio backend.\n"
        "You should be able to install this package using:\n"
        "pip install matrix-nio"
    )
    sys.exit(1)


class MatrixNioRoomError(RoomError):
    def __init__(self, message: str = None):
        if message is None:
            message = (
                "I currently do not support this request :(\n"
                "I still love you."
            )
        super().__init__(message)


class MatrixNioIdentifier(Identifier):
    def __init__(self, an_id: str):
        self._id = str(an_id)

    @property
    def id(self) -> str:
        return self._id

    def __unicode__(self) -> str:
        return str(self._id)

    def __eq__(self, other) -> bool:
        if hasattr(other, "id"):
            return self._id == other.id
        else:
            return False

    __str__ = __unicode__


# `MatrixNioPerson` is used for both 1-1 PMs and Group PMs.
class MatrixNioPerson(MatrixNioIdentifier, Person):
    def __init__(self, an_id: str, client: nio.Client, full_name: str, emails: list):
        super().__init__(an_id)
        self._full_name = full_name
        self._emails = emails
        self._client = client

    @property
    def person(self) -> str:
        """
        Maps to user_id
        :return: user_id
        """
        return self._id

    @property
    def fullname(self) -> str:
        """
        Maps to ProfileGetResponse.displayname
        :return: ProfileGetResponse.displayname
        """
        return self._full_name

    @property
    def nick(self) -> str:
        """
        Maps to ProfileGetResponse.displayname
        :return: ProfileGetResponse.displayname
        """
        return self._full_name

    @property
    def client(self) -> nio.Client:
        """
        Maps to AsyncClient
        :return: AsyncClient
        """
        return self._client

    @property
    def emails(self) -> list:
        """
        Maps to ProfileGetResponse.other_info['address']
        :return: ProfileGetResponse.other_info['address']
        """
        return self._emails

    @property
    def aclattr(self) -> str:
        """
        Maps to ProfileGetResponse.other_info['address']
        :return: ProfileGetResponse.other_info['address']
        """
        return ','.join(sorted(self._emails))


class MatrixNioRoom(MatrixNioIdentifier, Room):
    def __init__(self, an_id: str, client: nio.Client, title: str, subject: str = None):
        super().__init__(an_id)
        self._title = title
        self._subject = subject
        self._client = client
        self.matrix_room = self._client.rooms[an_id]

    @property
    def id(self) -> str:
        """
        Maps to MatrixRoom.room_id
        :return: MatrixRoom.room_id
        """
        return self._id

    @property
    def aclattr(self) -> str:
        """
        Maps to MatrixRoom.own_user_id
        :return: MatrixRoom.own_user_id
        """
        return self.matrix_room.own_user_id

    @property
    def subject(self) -> str:
        """
        Maps to MatrixRoom.topic
        :return: MatrixRoom.topic
        """
        return self.matrix_room.topic

    @property
    def title(self) -> str:
        """
        Maps to MatrixRoom.display_name
        :return: MatrixRoom.display_name
        """
        return self.matrix_room.display_name

    @property
    def exists(self) -> bool:
        rooms_list = list(self._client.rooms.keys())
        return self.id in rooms_list

    @property
    def joined(self) -> bool:
        joined_rooms = asyncio.get_event_loop().run_until_complete(self._client.joined_rooms())
        if isinstance(joined_rooms, JoinedRoomsError):
            raise ValueError(f"Error while fetching joined rooms {joined_rooms}")
        return self.id in joined_rooms.rooms

    def destroy(self) -> None:
        result = asyncio.get_event_loop().run_until_complete(self._client.room_forget(self.id))
        if isinstance(result, RoomForgetError):
            raise ValueError(f"Error while forgetting/destroying room {result}")

    async def join(self, username: str = None, password: str = None) -> None:
        result = None
        if self._client:
            result = await self._client.join(self.id)
        if isinstance(result, nio.responses.JoinError):
            raise MatrixNioRoomError(result)

    async def create(self) -> None:
        result = await self._client.room_create(
            name=self.title,
            topic=self.subject
        )
        if isinstance(result, nio.responses.RoomCreateError):
            raise MatrixNioRoomError(result)

    async def leave(self, reason: str = None) -> None:
        if self._client:
            result = await self._client.room_leave(self.id)
        if isinstance(result, nio.responses.RoomLeaveError):
            raise MatrixNioRoomError(result)

    @property
    def topic(self) -> str:
        """
        Maps to MatrixRoom.topic
        :return: MatrixRoom.topic
        """
        return self.matrix_room.topic

    @property
    def occupants(self) -> list:
        """
        Maps to MatrixRoom.users
        :return: MatrixRoom.users
        """
        users = self.matrix_room.users
        occupants = []
        for i in users:
            an_occupant = MatrixNioRoomOccupant(i.user_id, full_name=i.display_name, client=self._client)
            occupants.append(an_occupant)
        return occupants

    async def invite(self, *args: List[Any]) -> None:
        result_list = []
        for i in args[0]:
            result = await self._client.room_invite(i.user_id)
            result_list.append(result)
        if any(isinstance(x, nio.responses.RoomInviteError) for x in result_list):
            raise MatrixNioRoomError(result_list)


class MatrixNioRoomOccupant(MatrixNioPerson, RoomOccupant):
    """
    This class represents a person subscribed to a stream.
    """

    def __init__(self,
                 an_id: str,
                 full_name: str,
                 client: nio.Client,
                 emails: Optional[List[str]] = None,
                 room: MatrixNioRoom = None):
        super().__init__(an_id, full_name=full_name, emails=emails, client=client)
        self._room = room

    @property
    def room(self) -> Optional[MatrixNioRoom]:
        return self._room


class MatrixNioBackend(ErrBot):
    def __init__(self, config):
        super().__init__(config)
        self.has_synced = False
        self.identity = config.BOT_IDENTITY
        for key in ('email', 'auth_dict', 'site'):
            if key not in self.identity:
                log.fatal(
                    f"You need to supply the key `{key}` for me to use. `{key}` and its value "
                    "can be found in your bot's `matrixniorc` config file."
                )
                sys.exit(1)
        # Store the sync token in order to avoid replay of old messages.
        config = AsyncClientConfig(store_sync_tokens=True)
        self.client = nio.AsyncClient(
            self.identity['site'],
            self.identity['email'],
            config=config
        )

    def serve_once(self) -> bool:
        log.debug("Serve once")
        return asyncio.get_event_loop().run_until_complete(self._serve_once())

    async def _serve_once(self) -> bool:
        try:
            if not self.client.logged_in:
                log.info("Initializing connection")
                login_response = await self.client.login_raw(self.identity['auth_dict'])
                if isinstance(login_response, LoginError):
                    log.error(f"Failed login result: {login_response}")
                    raise ValueError(login_response)
                self.connect_callback()
                self.bot_identifier = await self.build_identifier(login_response.user_id)
                self.reset_reconnection_count()
            if self.has_synced:
                log.debug("Starting sync")
                await self.client.sync_forever(30000, full_state=True)
                log.debug("Sync finished")
                return False
            else:
                log.info("First sync, discarding previous messages")
                sync_response = await self.client.sync(full_state=True)
                if isinstance(sync_response, ErrorResponse):
                    log.exception("Error reading from Matrix Nio updates rooms.")
                    raise ValueError(sync_response)
                self.has_synced = True
                self.client.next_batch = sync_response.next_batch
                # Only setup callback after first sync in order to avoid processing previous messages
                self.client.add_event_callback(self.handle_message, nio.RoomMessageText)
                log.info("End of first sync, now starting normal operation")
                return False
        except (KeyboardInterrupt, StopIteration):
            log.info("Interrupt received, shutting down..")
            await self.client.logout()
            log.debug("Triggering disconnect callback.")
            self.disconnect_callback()
            return True

    def handle_message(self, room: nio.MatrixRoom, event: nio.Event) -> None:
        """
        Handles incoming messages.
        """
        log.debug(f"Handle room message\n"
                  f"Room: {room}\n"
                  f"Event: {event}")

        if not isinstance(event, nio.RoomMessageText):
            log.warning("Unhandled message type (not a text message) ignored")
            return

        message_instance = self.build_message(event.body)
        message_instance.frm = MatrixNioRoomOccupant(
            event.sender,
            full_name=room.user_name(event.sender),
            emails=[event.sender],
            client=self.client,
            room=room.room_id
        )
        room_instance = MatrixNioRoom(
            room.room_id,
            title=room.name,
            subject=room.display_name,
            client=self.client
        )
        message_instance.to = room_instance
        self.callback_message(message_instance)

    def send_message(self, msg: Message) -> RoomSendResponse:
        log.debug(f"Sending message {msg}")
        super().send_message(msg)
        result = self._send_message(msg)
        return result

    async def _send_message(self, msg: Message) -> RoomSendResponse:
        msg_data = {
            'msgtype': "m.text",
            'body': msg.body
        }
        result = await self.client.room_send(
            room_id=str(msg.to),
            message_type='m.room.message',
            content=msg_data
        )
        if isinstance(result, RoomSendResponse):
            return result
        else:
            raise ValueError(f"An exception occurred while trying to send the following message "
                             f"to {msg.to}: {msg.body}\n{result}")

    def connect_callback(self) -> None:
        # TODO implement this
        pass

    def disconnect_callback(self) -> None:
        # TODO implement this
        pass

    def is_from_self(self, msg: Message) -> bool:
        return msg.frm.id == self.client.user

    def change_presence(self, status: str = ONLINE, message: str = '') -> None:
        # TODO implement this
        # At this time, this backend doesn't support presence
        pass

    async def build_identifier(self, txtrep) -> MatrixNioPerson:
        log.debug(f"Build id : {txtrep}")
        profile = await asyncio.gather(
            self.client.get_profile(txtrep)
        )
        if len(profile) == 1 and isinstance(profile[0], nio.responses.ProfileGetResponse):
            return MatrixNioPerson(txtrep,
                                   full_name=profile[0].displayname,
                                   emails=[txtrep],
                                   client=self.client)
        else:
            raise ValueError(f"An error occured while fetching identifier: {profile}")

    def build_reply(self, msg, text=None, private=False, threaded=False) -> Message:
        # TODO : Include marker for threaded response
        response = self.build_message(f"{msg.body}\n{text}")
        response.to = msg.frm
        return response

    @property
    def mode(self) -> str:
        return "matrix-nio"

    def query_room(self, room) -> MatrixNioRoom:
        rooms = asyncio.get_event_loop().run_until_complete(self.rooms())
        chosen_room = rooms[room]
        return chosen_room

    def rooms(self) -> Coroutine[Any, Any, dict]:
        result = self._rooms()
        return result

    async def _rooms(self) -> dict:
        result = await asyncio.gather(
            self.client.joined_rooms()
        )
        if len(result) == 1 and isinstance(result[0], nio.responses.JoinedRoomsResponse):
            result = result[0]
        else:
            raise ValueError(f"An error occured while fetching joined rooms: {result}")
        rooms = {}
        for room_name in result.rooms:
            a_room = MatrixNioRoom(room_name, self.client, title=room_name)
            rooms[a_room.id] = a_room
        return rooms

    def prefix_groupchat_reply(self, message: Message, identifier: MatrixNioPerson) -> None:
        message.body = f"@{identifier.fullname} {message.body}"
