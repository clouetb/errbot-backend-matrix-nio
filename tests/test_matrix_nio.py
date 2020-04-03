import logging
import unittest
from unittest import TestCase
from unittest import mock
from unittest.mock import call

import aiounittest
import nio
from nio import MatrixUser

import matrix_nio

matrix_nio.log.setLevel(logging.DEBUG)


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

    def test_matrix_nio_room_topic(self):
        self.assertEqual(self.room1.topic, self.topic)

    def test_matrix_nio_room_occupants(self):
        self.assertEqual(self.room1.occupants, self.occupants)

    async def test_matrix_nio_room_invite(self):
        client_invite = mock.Mock(return_value=aiounittest.futurized(nio.responses.RoomInviteResponse))
        self.room1._client.room_invite = client_invite
        await self.room1.invite(self.users)
        client_invite.assert_has_calls([call("12345"), call("54321")])


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
                                                               self.emails,
                                                               self.client,
                                                               self.room1)

    def test_matrix_nio_room_occupant(self):
        room_id1 = "test_room"
        subject1 = "test_room"
        room1 = matrix_nio.MatrixNioRoom(room_id1,
                                         title=self.title,
                                         client=self.client,
                                         subject=subject1)
        self.assertEqual(self.room_occupant1.room, room1)


if __name__ == '__main__':
    unittest.main()
