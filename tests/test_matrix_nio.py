import asyncio
import copy
import json
import logging
import unittest
from unittest import TestCase
from unittest import mock
from unittest.mock import call

import aiounittest
import nio
from errbot import Message
from errbot.core import ErrBot
from nio import MatrixUser, JoinedRoomsResponse, JoinedRoomsError, ProfileGetResponse, ProfileGetError, \
    RoomSendResponse, ErrorResponse, RoomMessageText, RoomMessageEmote, LoginResponse, LoginError, SyncResponse

import matrix_nio

matrix_nio.log.setLevel(logging.DEBUG)
fucking_string = """
{
    "device_one_time_keys_count": {},
    "next_batch": "s526_47314_0_7_1_1_1_11444_1",
    "device_lists": {
    "changed": [
      "@example:example.org"
    ],
    "left": []
    },

    "rooms": {
        "invite": {},
        "join": {
            "!SVkFJHzfwvuaIEawgC:localhost": {
                "account_data": {
                    "events": []
                },
                "ephemeral": {
                    "events": [
                        {
                            "content": {
                                "$151680659217152dPKjd:localhost": {
                                    "m.read": {
                                        "@example:localhost": {
                                            "ts": 1516809890615
                                        }
                                    }
                                }
                            },
                            "type": "m.receipt"
                        }
                    ]
                },
                "state": {
                    "events": [
                        {
                            "content": {
                                "join_rule": "public"
                            },
                            "event_id": "$15139375514WsgmR:localhost",
                            "origin_server_ts": 1513937551539,
                            "sender": "@example:localhost",
                            "state_key": "",
                            "type": "m.room.join_rules",
                            "unsigned": {
                                "age": 7034220355
                            }
                        },
                        {
                            "content": {
                                "avatar_url": null,
                                "displayname": "example",
                                "membership": "join"
                            },
                            "event_id": "$151800140517rfvjc:localhost",
                            "membership": "join",
                            "origin_server_ts": 1518001405556,
                            "sender": "@example:localhost",
                            "state_key": "@example:localhost",
                            "type": "m.room.member",
                            "unsigned": {
                                "age": 2970366338,
                                "replaces_state": "$151800111315tsynI:localhost"
                            }
                        },
                        {
                            "content": {
                                "history_visibility": "shared"
                            },
                            "event_id": "$15139375515VaJEY:localhost",
                            "origin_server_ts": 1513937551613,
                            "sender": "@example:localhost",
                            "state_key": "",
                            "type": "m.room.history_visibility",
                            "unsigned": {
                                "age": 7034220281
                            }
                        },
                        {
                            "content": {
                                "creator": "@example:localhost"
                            },
                            "event_id": "$15139375510KUZHi:localhost",
                            "origin_server_ts": 1513937551203,
                            "sender": "@example:localhost",
                            "state_key": "",
                            "type": "m.room.create",
                            "unsigned": {
                                "age": 7034220691
                            }
                        },
                        {
                            "content": {
                                "aliases": [
                                    "#tutorial:localhost"
                                ]
                            },
                            "event_id": "$15139375516NUgtD:localhost",
                            "origin_server_ts": 1513937551720,
                            "sender": "@example:localhost",
                            "state_key": "localhost",
                            "type": "m.room.aliases",
                            "unsigned": {
                                "age": 7034220174
                            }
                        },
                        {
                            "content": {
                                "topic": "\ud83d\ude00"
                            },
                            "event_id": "$151957878228ssqrJ:localhost",
                            "origin_server_ts": 1519578782185,
                            "sender": "@example:localhost",
                            "state_key": "",
                            "type": "m.room.topic",
                            "unsigned": {
                                "age": 1392989709,
                                "prev_content": {
                                    "topic": "test"
                                },
                                "prev_sender": "@example:localhost",
                                "replaces_state": "$151957069225EVYKm:localhost"
                            }
                        },
                        {
                            "content": {
                                "ban": 50,
                                "events": {
                                    "m.room.avatar": 50,
                                    "m.room.canonical_alias": 50,
                                    "m.room.history_visibility": 100,
                                    "m.room.name": 50,
                                    "m.room.power_levels": 100
                                },
                                "events_default": 0,
                                "invite": 0,
                                "kick": 50,
                                "redact": 50,
                                "state_default": 50,
                                "users": {
                                    "@example:localhost": 100
                                },
                                "users_default": 0
                            },
                            "event_id": "$15139375512JaHAW:localhost",
                            "origin_server_ts": 1513937551359,
                            "sender": "@example:localhost",
                            "state_key": "",
                            "type": "m.room.power_levels",
                            "unsigned": {
                                "age": 7034220535
                            }
                        },
                        {
                            "content": {
                                "alias": "#tutorial:localhost"
                            },
                            "event_id": "$15139375513VdeRF:localhost",
                            "origin_server_ts": 1513937551461,
                            "sender": "@example:localhost",
                            "state_key": "",
                            "type": "m.room.canonical_alias",
                            "unsigned": {
                                "age": 7034220433
                            }
                        },
                        {
                            "content": {
                                "avatar_url": null,
                                "displayname": "example2",
                                "membership": "join"
                            },
                            "event_id": "$152034824468gOeNB:localhost",
                            "membership": "join",
                            "origin_server_ts": 1520348244605,
                            "sender": "@example2:localhost",
                            "state_key": "@example2:localhost",
                            "type": "m.room.member",
                            "unsigned": {
                                "age": 623527289,
                                "prev_content": {
                                    "membership": "leave"
                                },
                                "prev_sender": "@example:localhost",
                                "replaces_state": "$152034819067QWJxM:localhost"
                            }
                        }
                    ]
                },
                "timeline": {
                    "events": [
                        {
                            "content": {
                                "body": "baba",
                                "format": "org.matrix.custom.html",
                                "formatted_body": "<strong>baba</strong>",
                                "msgtype": "m.text"
                            },
                            "event_id": "$152037280074GZeOm:localhost",
                            "origin_server_ts": 1520372800469,
                            "sender": "@example:localhost",
                            "type": "m.room.message",
                            "unsigned": {
                                "age": 598971425
                            }
                        }
                    ],
                    "limited": true,
                    "prev_batch": "t392-516_47314_0_7_1_1_1_11444_1"
                },
                "unread_notifications": {
                    "highlight_count": 0,
                    "notification_count": 11
                }
            }
        },
        "leave": {}
    },
    "to_device": {
        "events": []
    }
}

"""

class TestMatrixNioRoomError(TestCase):
    def test_room_error_with_value(self):
        room_error = matrix_nio.MatrixNioRoomError("A message")
        self.assertEqual(room_error.args[0], "A message")

    def test_room_error_with_none(self):
        room_error = matrix_nio.MatrixNioRoomError(None)
        self.assertEqual(room_error.args[0],
                         "I currently do not support this request :(\n"
                         "I still love you.")


class TestMatrixNioIdentifier(TestCase):
    def test_matrix_nio_identifier_string(self):
        value = "12345"
        identifier = matrix_nio.MatrixNioIdentifier(value)
        self.assertEqual(identifier.id, value)

    def test_matrix_nio_identifier_unicode_string(self):
        value = "12345éàç€"
        identifier = matrix_nio.MatrixNioIdentifier(value)
        self.assertEqual(str(identifier), value)

    def test_matrix_nio_identifier_int(self):
        value = 12345
        identifier = matrix_nio.MatrixNioIdentifier(value)
        self.assertEqual(identifier.id, str(value))

    def test_matrix_nio_identifier_other(self):
        value_string = "12345"
        value_int = 12345
        identifier_int = matrix_nio.MatrixNioIdentifier(value_int)
        identifier_string = matrix_nio.MatrixNioIdentifier(value_string)
        self.assertEqual(identifier_int, identifier_string)


class TestMatrixNioPerson(TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        self.client.rooms = {"test_room": "empty_room", "other_test_room": "also_empty_room"}

        self.person_id = "12345"
        self.full_name = "Charles de Gaulle"
        self.emails = ["charles@colombay.fr", "charles.degaulle@elysee.fr"]
        self.person1 = matrix_nio.MatrixNioPerson(self.person_id,
                                                  client=self.client,
                                                  full_name=self.full_name,
                                                  emails=self.emails)

    def test_matrix_nio_person(self):
        self.assertEqual(str(self.person1), self.person_id)

    def test_matrix_nio_person_id(self):
        identifier = matrix_nio.MatrixNioIdentifier("12345")
        self.assertEqual(self.person1, identifier)

    def test_matrix_nio_person_equality(self):
        person2 = matrix_nio.MatrixNioPerson(12345,
                                             client=self.client,
                                             full_name="Not Charles de Gaulle",
                                             emails=[])
        self.assertEqual(self.person1, person2)

    def test_matrix_nio_person_inequality(self):
        person2 = matrix_nio.MatrixNioPerson(54321,
                                             client=self.client,
                                             full_name=self.full_name,
                                             emails=self.emails)
        self.assertNotEqual(self.person1, person2)

    def test_matrix_nio_person_acls(self):
        acls = "charles.degaulle@elysee.fr,charles@colombay.fr"
        self.assertEqual(self.person1.aclattr, acls)

    def test_matrix_nio_person_emails(self):
        emails = ["charles@colombay.fr", "charles.degaulle@elysee.fr"]
        self.assertEqual(self.person1.emails, emails)

    def test_matrix_nio_person_person(self):
        self.assertEqual(self.person1.person, self.person_id)

    def test_matrix_nio_person_full_name(self):
        self.assertEqual(self.person1.fullname, self.full_name)

    def test_matrix_nio_person_nick(self):
        self.assertEqual(self.person1.nick, self.full_name)

    def test_matrix_nio_person_client(self):
        self.assertEqual(self.person1.client, self.client)


class TestMatrixNioRoom(aiounittest.AsyncTestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        self.owner = "an_owner"
        self.room_id = "test_room"
        self.matrix_room1 = nio.MatrixRoom(self.owner, self.room_id)
        self.client.rooms = {"test_room": self.matrix_room1, "other_test_room": "also_empty_room"}

        self.subject = "test_room"
        self.title = "A title"
        self.topic = "a_topic"
        self.display_name = "a_display_name"
        self.room1 = matrix_nio.MatrixNioRoom(self.room_id,
                                              client=self.client,
                                              title=self.title,
                                              subject=self.subject)
        self.users = [
            MatrixUser("12345", display_name="Charles de Gaulle"),
            MatrixUser("54321", display_name="Georges Pompidou")
        ]
        self.occupants = [
            matrix_nio.MatrixNioRoomOccupant("12345", "Charles de Gaulle", self.client),
            matrix_nio.MatrixNioRoomOccupant("54321", "Georges Pompidou", self.client)
        ]
        self.room1.matrix_room.users = self.users
        self.room1.matrix_room.own_user_id = self.owner
        self.room1.matrix_room.topic = self.topic
        self.room1.matrix_room.name = self.display_name

    def test_matrix_nio_room_creation(self):
        self.assertEqual(str(self.room1), self.room_id)

    def test_matrix_nio_room_aclattr(self):
        self.assertEqual(self.room1.aclattr, self.owner)

    def test_matrix_nio_room_topic(self):
        self.assertEqual(self.room1.topic, self.topic)

    def test_matrix_nio_room_title(self):
        self.assertEqual(self.room1.title, self.display_name)

    async def test_matrix_nio_room_join(self):
        client_join = mock.Mock(return_value=aiounittest.futurized("whatever"))
        self.room1._client.join = client_join
        await self.room1.join("discarded", "discarded")
        client_join.assert_called_once_with(self.room_id)

    async def test_matrix_nio_room_join_error(self):
        client_join = mock.Mock(return_value=aiounittest.futurized(nio.responses.JoinError("Join Error")))
        self.room1._client.join = client_join
        with self.assertRaises(matrix_nio.MatrixNioRoomError):
            await self.room1.join("discarded", "discarded")

    async def test_matrix_nio_room_create(self):
        client_create = mock.Mock(return_value=aiounittest.futurized("whatever"))
        self.room1._client.room_create = client_create
        await self.room1.create()
        client_create.assert_called_once_with(name=self.display_name, topic=self.topic)

    async def test_matrix_nio_room_create_error(self):
        client_create = mock.Mock(return_value=aiounittest.futurized(nio.responses.RoomCreateError("Create Error")))
        self.room1._client.room_create = client_create
        with self.assertRaises(matrix_nio.MatrixNioRoomError):
            await self.room1.create()

    async def test_matrix_nio_room_leave(self):
        client_leave = mock.Mock(return_value=aiounittest.futurized("whatever"))
        self.room1._client.room_leave = client_leave
        await self.room1.leave("a very good reason")
        client_leave.assert_called_once_with(self.room_id)

    async def test_matrix_nio_room_leave_error(self):
        client_leave = mock.Mock(return_value=aiounittest.futurized(nio.responses.RoomLeaveError("Leave Error")))
        self.room1._client.room_leave = client_leave
        with self.assertRaises(matrix_nio.MatrixNioRoomError):
            await self.room1.leave("a very good reason")

    def test_matrix_nio_room_occupants(self):
        self.assertEqual(self.room1.occupants, self.occupants)

    async def test_matrix_nio_room_invite(self):
        client_invite = mock.Mock(
            return_value=aiounittest.futurized(
                nio.responses.RoomInviteResponse()
            )
        )
        self.room1._client.room_invite = client_invite
        await self.room1.invite(self.users)
        client_invite.assert_has_calls([call("12345"), call("54321")])

    async def test_matrix_nio_room_invite_error(self):
        client_invite = mock.Mock(
            return_value=aiounittest.futurized(
                nio.responses.RoomInviteError("Invite Error")
            )
        )
        self.room1._client.room_invite = client_invite
        with self.assertRaises(matrix_nio.MatrixNioRoomError):
            await self.room1.invite(self.users)
        client_invite.assert_has_calls([call("12345"), call("54321")])

    def test_matrix_nio_room_exists(self):
        matrix_client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        nio_room1 = nio.MatrixRoom("nio_room1", "room1_owner")
        nio_room2 = nio.MatrixRoom("nio_room2", "room2_owner")
        matrix_rooms = {
            "nio_room1": nio_room1,
            "nio_room2": nio_room2
        }
        matrix_client.rooms = matrix_rooms
        errbot_nio_room1 = matrix_nio.MatrixNioRoom("nio_room1",
                                                    client=matrix_client,
                                                    title="nio_room1 title",
                                                    subject="nio_room1 subject")
        errbot_nio_room2 = matrix_nio.MatrixNioRoom("nio_room2",
                                                    client=matrix_client,
                                                    title="nio_room2 title",
                                                    subject="nio_room2 subject")
        del matrix_client.rooms[errbot_nio_room2.id]
        result1 = errbot_nio_room1.exists
        result2 = errbot_nio_room2.exists
        self.assertTrue(result1)
        self.assertFalse(result2)

    def test_matrix_nio_room_joined(self):
        matrix_client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        joined_nio_room1 = nio.MatrixRoom("nio_room1", "room1_owner")
        joined_nio_room2 = nio.MatrixRoom("nio_room2", "room2_owner")
        joined_matrix_rooms = {
            "nio_room1": joined_nio_room1,
            "nio_room2": joined_nio_room2
        }
        matrix_client.rooms = joined_matrix_rooms
        errbot_nio_room1 = matrix_nio.MatrixNioRoom("nio_room1",
                                                    client=matrix_client,
                                                    title="nio_room1 title",
                                                    subject="nio_room1 subject")
        errbot_nio_room2 = matrix_nio.MatrixNioRoom("nio_room2",
                                                    client=matrix_client,
                                                    title="nio_room2 title",
                                                    subject="nio_room2 subject")
        matrix_client.joined_rooms = mock.Mock(
            return_value=aiounittest.futurized(
                JoinedRoomsResponse.from_dict({
                    "joined_rooms": ["nio_room1", "nio_room2"]
                })

            )
        )
        # joined = True
        result1 = errbot_nio_room1.joined
        self.assertTrue(result1)
        matrix_client.joined_rooms.assert_called_once()
        matrix_client.joined_rooms = mock.Mock(
            return_value=aiounittest.futurized(
                JoinedRoomsResponse.from_dict({
                    "joined_rooms": ["nio_room1"]
                })

            )
        )
        # joined = false
        result2 = errbot_nio_room2.joined
        self.assertFalse(result2)
        matrix_client.joined_rooms.assert_called_once()

    def test_matrix_nio_joined_room_error(self):
        matrix_client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        joined_nio_room1 = nio.MatrixRoom("nio_room1", "room1_owner")
        joined_matrix_rooms = {
            "nio_room1": joined_nio_room1
        }
        matrix_client.rooms = joined_matrix_rooms
        errbot_nio_room1 = matrix_nio.MatrixNioRoom("nio_room1",
                                                    client=matrix_client,
                                                    title="nio_room1 title",
                                                    subject="nio_room1 subject")
        matrix_client.joined_rooms = mock.Mock(
            return_value=aiounittest.futurized(
                JoinedRoomsError.from_dict({
                    "errcode": "ERROR_FETCHING_JOINED_ROOMS",
                    "error": "Error fetching joined rooms",
                    "retry_after_ms": 10000

                })

            )
        )
        result = None
        with self.assertRaises(ValueError):
            result = errbot_nio_room1.joined
        self.assertIsNone(result)
        matrix_client.joined_rooms.assert_called_once()

    def test_matrix_nio_room_destroy(self):
        pass

    def test_matrix_nio_room_destroy_error(self):
        pass


class TestMatrixNioRoomOccupant(TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        self.client.rooms = {"test_room": "empty_room", "other_test_room": "also_empty_room"}

        self.room_id = "test_room"
        self.subject = "test_room"
        self.title = "A title"
        self.room1 = matrix_nio.MatrixNioRoom(self.room_id,
                                              client=self.client,
                                              title=self.title,
                                              subject=self.subject)

        self.person_id = "12345"
        self.full_name = "Charles de Gaulle"
        self.emails = ["charles@colombay.fr", "charles.degaulle@elysee.fr"]
        self.room_occupant1 = matrix_nio.MatrixNioRoomOccupant(self.person_id,
                                                               self.full_name,
                                                               self.client,
                                                               self.emails,
                                                               self.room1)

    def test_matrix_nio_room_occupant(self):
        room_id1 = "test_room"
        subject1 = "test_room"
        room1 = matrix_nio.MatrixNioRoom(room_id1,
                                         title=self.title,
                                         client=self.client,
                                         subject=subject1)
        self.assertEqual(self.room_occupant1.room, room1)


class TestMatrixNioBackend(aiounittest.AsyncTestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

        class Configuration(object):
            pass

        self.bot_config = Configuration()
        self.bot_config.BOT_PREFIX = "BotPrefix"
        self.bot_config.BOT_ASYNC = False
        self.bot_config.BOT_ALT_PREFIX_CASEINSENSITIVE = "botprefix"
        self.bot_config.BOT_ALT_PREFIXES = "anotherbotprefix"
        self.bot_config.BOT_IDENTITY = {
            "email": "test@test.org",
            "site": "https://test.test.org",
            "auth_dict": {
                "type": "m.login.password",
                "identifier": {
                    "type": "m.id.thirdparty",
                    "medium": "email",
                    "address": "test@test.org"
                },
                "password": "SuperSecretPassword",
                "initial_device_display_name": f"test-bot"
            }
        }

    def test_matrix_nio_backend(self):
        test_backend = matrix_nio.MatrixNioBackend(self.bot_config)
        self.assertIsInstance(test_backend.client, nio.Client)
        self.assertIsInstance(test_backend.client.config, nio.AsyncClientConfig)

    def test_matrix_nio_backend_startup_error(self):
        configuration_copy = copy.deepcopy(self.bot_config)
        del (configuration_copy.BOT_IDENTITY["email"])
        with self.assertRaises(SystemExit):
            matrix_nio.MatrixNioBackend(configuration_copy)

        configuration_copy = copy.deepcopy(self.bot_config)
        del (configuration_copy.BOT_IDENTITY["auth_dict"])
        with self.assertRaises(SystemExit):
            matrix_nio.MatrixNioBackend(configuration_copy)

        configuration_copy = copy.deepcopy(self.bot_config)
        del (configuration_copy.BOT_IDENTITY["site"])
        with self.assertRaises(SystemExit):
            matrix_nio.MatrixNioBackend(configuration_copy)

    def test_matrix_nio_backend_serve_once_logged_in_has_synced(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        backend.has_synced = True
        # Needed for ensuring that backend.client.logged_in = True
        backend.client.access_token = True
        sync_forever_mock = mock.Mock(
            return_value=aiounittest.futurized(
                True
            )
        )
        backend.client.sync_forever = sync_forever_mock
        backend.serve_once()
        sync_forever_mock.assert_called_once_with(30000, full_state=True)

    def test_matrix_nio_backend_serve_once_logged_in_has_not_synced(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        # Needed for ensuring that backend.client.logged_in = True
        backend.client.access_token = True

        with open("sync.json") as json_file:
            data = json.loads(json_file.read())

        sync_mock = mock.Mock(
            return_value=aiounittest.futurized(
                SyncResponse.from_dict(data)
            )
        )
        backend.client.sync = sync_mock
        backend.serve_once()
        self.assertTrue(backend.has_synced)
        self.assertEqual(backend.client.next_batch, data["next_batch"])
        sync_mock.assert_called_once_with(full_state=True)

    def test_matrix_nio_backend_serve_once_logged_keyboard_interrupt(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        backend.has_synced = True
        # Needed for ensuring that backend.client.logged_in = True
        backend.client.access_token = True
        sync_forever_mock = mock.Mock(
            side_effect=aiounittest.futurized(
                KeyboardInterrupt()
            )
        )
        backend.client.logout = mock.Mock(
            return_value=aiounittest.futurized(
                True
            )
        )
        backend.client.sync_forever = sync_forever_mock
        backend.serve_once()
        sync_forever_mock.assert_called_once_with(30000, full_state=True)
        backend.client.logout.assert_called_once()

    def test_matrix_nio_backend_serve_once_not_logged_in_has_synced(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        backend.has_synced = True
        user_id = "@example:localhost"
        login_response = LoginResponse.from_dict({
            "user_id": user_id,
            "device_id": "device_id",
            "access_token": "12345",
        })
        login_response_mock = mock.Mock(
            return_value=aiounittest.futurized(
                login_response
            )
        )
        backend.client.login_raw = login_response_mock
        test_name = "Test Name"
        backend.client.get_profile = mock.Mock(
            return_value=aiounittest.futurized(
                ProfileGetResponse.from_dict({
                    "displayname": test_name,
                    "avatar_url": "http://test.org/avatar.png"
                })
            )
        )
        sync_forever_mock = mock.Mock(
            return_value=aiounittest.futurized(
                True
            )
        )
        backend.client.sync_forever = sync_forever_mock
        backend.serve_once()
        sync_forever_mock.assert_called_once_with(30000, full_state=True)
        backend.client.get_profile.assert_called_once_with(user_id)
        login_response_mock.assert_called_once_with(self.bot_config.BOT_IDENTITY["auth_dict"])

    def test_matrix_nio_backend_serve_once_login_error(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        user_id = "@example:localhost"
        login_response = LoginError.from_dict({
            "errcode": "ERROR_LOGGING_IN",
            "error": "Error logging in",
            "retry_after_ms": 10000
        })
        login_raw_mock = mock.Mock(
            return_value=aiounittest.futurized(
                login_response
            )
        )
        backend.client.login_raw = login_raw_mock
        with self.assertRaises(ValueError):
            backend.serve_once()
        login_raw_mock.assert_called_once_with(self.bot_config.BOT_IDENTITY["auth_dict"])

    def test_matrix_nio_backend_serve_once_not_logged_in_has_not_synced_error_sync(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        backend.client.access_token = True
        user_id = "@example:localhost"
        login_response = LoginResponse.from_dict({
            "user_id": user_id,
            "device_id": "device_id",
            "access_token": "12345",
        })
        login_response_mock = mock.Mock(
            return_value=aiounittest.futurized(
                login_response
            )
        )
        backend.client.login_raw = login_response_mock
        sync_mock = mock.Mock(
            return_value=aiounittest.futurized(
                ErrorResponse.from_dict({
                    "errcode": "ERROR_SYNCING",
                    "error": "Error syncing",
                    "retry_after_ms": 10000
                })
            )
        )
        backend.client.sync = sync_mock
        with self.assertRaises(ValueError):
            backend.serve_once()
        sync_mock.assert_called_once_with(full_state=True)

    def test_matrix_nio_backend_handle_message(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org",
                                         user="test_user",
                                         device_id="test_device"
                                         )
        backend.client.rooms = {"test_room": "Test Room", "other_test_room": "Test Room"}
        message_body = "Test message"
        test_message = RoomMessageText.from_dict({
            "content": {
                "body": message_body,
                "msgtype": "m.text"
            },
            "event_id": "$15163623196QOZxj:localhost",
            "origin_server_ts": 1516362319505,
            "room_id": "!SVkFJHzfwvuaIEawgC:localhost",
            "sender": "@example:localhost",
            "type": "m.room.message",
            "unsigned": {
                "age": 43464955731
            },
            "user_id": "@example:localhost",
            "age": 43464955731
        })
        test_room = nio.MatrixRoom("test_room",
                                   "test_user")
        test_message.to = test_room
        callback = mock.Mock()
        ErrBot.callback_message = callback
        backend.build_message = mock.Mock()
        backend.handle_message(test_room, test_message)
        callback.assert_called_once()
        backend.build_message.assert_called_once_with(test_message.body)

    def test_matrix_nio_backend_handle_unsupported_message(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org",
                                         user="test_user",
                                         device_id="test_device"
                                         )
        backend.client.rooms = {"test_room": "Test Room", "other_test_room": "Test Room"}
        message_body = "Test message"
        test_message = RoomMessageEmote.from_dict({
            "content": {
                "body": message_body,
                "msgtype": "m.emote"
            },
            "event_id": "$15163623196QOZxj:localhost",
            "origin_server_ts": 1516362319505,
            "room_id": "!SVkFJHzfwvuaIEawgC:localhost",
            "sender": "@example:localhost",
            "type": "m.room.message",
            "unsigned": {
                "age": 43464955731
            },
            "user_id": "@example:localhost",
            "age": 43464955731
        })
        test_room = nio.MatrixRoom("test_room",
                                   "test_user")
        test_message.to = test_room
        callback = mock.Mock()
        ErrBot.callback_message = callback
        backend.handle_message(test_room, test_message)
        callback.assert_not_called()

    async def test_matrix_nio_backend_send_message(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        test_server = "test.matrix.org"
        test_user = f"@test_user:{test_server}"
        event_id = "1234567890"
        room_id = "test_room"
        backend.client = nio.AsyncClient(test_server, user=test_user, device_id="test_device")
        backend.client.rooms = {"test_room": "Test Room", "other_test_room": "Test Room"}
        ErrBot.send_message = mock.Mock()
        backend.client.room_send = mock.Mock(
            return_value=aiounittest.futurized(
                RoomSendResponse.from_dict({
                    "event_id": event_id
                },
                    room_id)
            )
        )
        message_text = "Test message"
        test_message = Message(message_text,
                               matrix_nio.MatrixNioPerson("an_id",
                                                          client=backend.client,
                                                          emails=["test@test.org"],
                                                          full_name=""
                                                          )
                               )
        test_message.to = matrix_nio.MatrixNioRoom("test_room",
                                                   client=backend.client,
                                                   title="A title")
        result = await asyncio.gather(
            backend.send_message(test_message)
        )
        result = result[0]
        self.assertIsInstance(result, RoomSendResponse)
        self.assertEqual(result.room_id, room_id)
        self.assertEqual(result.event_id, event_id)
        # TODO: Add assert called once with
        backend.client.room_send.assert_called_once()

    async def test_matrix_nio_backend_send_message_error(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        test_server = "test.matrix.org"
        test_user = f"@test_user:{test_server}"
        event_id = "1234567890"
        room_id = "test_room"
        backend.client = nio.AsyncClient(test_server, user=test_user, device_id="test_device")
        backend.client.rooms = {"test_room": "Test Room", "other_test_room": "Test Room"}
        ErrBot.send_message = mock.Mock()
        backend.client.room_send = mock.Mock(
            return_value=aiounittest.futurized(
                ErrorResponse.from_dict({
                    "errcode": "ERROR_SENDING_MESSAGE",
                    "error": "Error sending message",
                    "retry_after_ms": 10000
                })
            )
        )
        message_text = "Test message"
        test_message = Message(message_text,
                               matrix_nio.MatrixNioPerson("an_id",
                                                          client=backend.client,
                                                          emails=["test@test.org"],
                                                          full_name=""
                                                          )
                               )
        test_message.to = matrix_nio.MatrixNioRoom("test_room",
                                                   client=backend.client,
                                                   title="A title")
        with self.assertRaises(ValueError):
            result = await asyncio.gather(
                backend.send_message(test_message)
            )
        backend.client.room_send.assert_called_once()
        # TODO: Add assert called once with

    def test_matrix_nio_backend_is_from_self(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        test_user_id = "test_user"
        backend.client = nio.AsyncClient("test.matrix.org",
                                         user=test_user_id,
                                         device_id="test_device"
                                         )
        message_text = "Test message"
        test_message = Message(message_text,
                               matrix_nio.MatrixNioPerson(test_user_id,
                                                          client=backend.client,
                                                          emails=["test@test.org"],
                                                          full_name=""
                                                          )
                               )
        self.assertTrue(backend.is_from_self(test_message))

    def test_matrix_nio_backend_is_not_from_self(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        test_user_id = "test_user"
        backend.client = nio.AsyncClient("test.matrix.org",
                                         user=test_user_id,
                                         device_id="test_device"
                                         )
        message_text = "Test message"
        response_text = "A response"
        test_message = Message(message_text,
                               matrix_nio.MatrixNioPerson("another_test_user_id",
                                                          client=backend.client,
                                                          emails=["test@test.org"],
                                                          full_name=""
                                                          )
                               )
        self.assertFalse(backend.is_from_self(test_message))

    async def test_matrix_nio_backend_build_identifier(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org",
                                         user="test_user",
                                         device_id="test_device"
                                         )
        test_name = "Test Name"
        backend.client.get_profile = mock.Mock(
            return_value=aiounittest.futurized(
                ProfileGetResponse.from_dict({
                    "displayname": test_name,
                    "avatar_url": "http://test.org/avatar.png"
                })
            )
        )
        test_id = "test_id"
        test_identifier = await asyncio.gather(
            backend.build_identifier(test_id)
        )
        test_identifier = test_identifier[0]
        self.assertIsInstance(test_identifier, matrix_nio.MatrixNioPerson)
        self.assertEqual(test_identifier.id, test_id)
        self.assertEqual(test_identifier.fullname, test_name)

    async def test_matrix_nio_backend_build_identifier_error(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org",
                                         user="test_user",
                                         device_id="test_device"
                                         )
        backend.client.get_profile = mock.Mock(
            return_value=aiounittest.futurized(
                ProfileGetError.from_dict({
                    "errcode": "ERROR_GETTING_PROFILE",
                    "error": "Error fetching profile",
                    "retry_after_ms": 10000
                })
            )
        )
        test_id = "test_id"
        with self.assertRaises(ValueError):
            test_identifier = await asyncio.gather(
                backend.build_identifier(test_id)
            )

    def test_matrix_nio_backend_build_reply(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org",
                                         user="test_user",
                                         device_id="test_device"
                                         )
        message_text = "Test message"
        response_text = "A response"
        test_message = Message(message_text,
                               matrix_nio.MatrixNioPerson("an_id",
                                                          client=backend.client,
                                                          emails=["test@test.org"],
                                                          full_name=""
                                                          )
                               )
        response = backend.build_reply(test_message, response_text)
        self.assertIsInstance(response, Message)
        self.assertEqual(response.to, test_message.frm)
        self.assertEqual(response.body, f"{message_text}\n{response_text}")

    def test_matrix_nio_backend_mode(self):
        mode = matrix_nio.MatrixNioBackend(self.bot_config).mode
        self.assertEqual(mode, "matrix-nio")

    def test_matrix_nio_backend_query_room(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        room_id1 = "test_room"
        room_id2 = "another_test_room"
        backend.client.rooms = {
            room_id1: room_id1,
            room_id2: room_id2
        }

        backend.client.joined_rooms = mock.Mock(
            return_value=aiounittest.futurized(
                JoinedRoomsResponse.from_dict({
                    "joined_rooms": [room_id1, room_id2]
                })
            )
        )
        result_room1 = backend.query_room(room_id1)
        result_room2 = backend.query_room(room_id2)
        self.assertEqual(result_room1.id, room_id1)
        self.assertEqual(result_room2.id, room_id2)

    async def test_matrix_nio_backend_rooms(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        room_id1 = "test_room"
        room_id2 = "another_test_room"
        backend.client.rooms = {
            room_id1: room_id1,
            room_id2: room_id2
        }

        backend.client.joined_rooms = mock.Mock(
            return_value=aiounittest.futurized(
                JoinedRoomsResponse.from_dict({
                    "joined_rooms": [room_id1, room_id2]
                })
            )
        )

        result = await asyncio.gather(
            backend.rooms()
        )
        result = result[0]
        result = list(result.keys())
        self.assertIn(room_id1, result)
        self.assertIn(room_id2, result)

    async def test_matrix_nio_backend_rooms_error(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")

        backend.client.joined_rooms = mock.Mock(
            return_value=aiounittest.futurized(
                JoinedRoomsError.from_dict({
                    "errcode": "ERROR_FETCHING_SUBSCRIBED_ROOMS",
                    "error": "Error fetching subscribed rooms",
                    "retry_after_ms": 10000
                }
                )
            )
        )
        with self.assertRaises(ValueError):
            result = await asyncio.gather(
                backend.rooms()
            )

    def test_matrix_nio_backend_prefix_groupchat_reply(self):
        backend = matrix_nio.MatrixNioBackend(self.bot_config)
        backend.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        full_name = "Charles de Gaulle"
        person = matrix_nio.MatrixNioPerson("an_id", backend.client, full_name, ["test@test.org"])
        message = Message("A message")
        message_body = f"@{person.fullname} {message.body}"
        backend.prefix_groupchat_reply(message, person)
        self.assertEqual(message.body, message_body)


if __name__ == '__main__':
    unittest.main()
