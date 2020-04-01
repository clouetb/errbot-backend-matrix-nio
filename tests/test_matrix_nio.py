import unittest
from unittest import TestCase

import nio

import matrix_nio


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
        self.person_id = "12345"
        self.full_name = "Charles de Gaulle"
        self.emails = ["charles@colombay.fr", "charles.degaulle@elysee.fr"]
        self.person1 = matrix_nio.MatrixNioPerson(self.person_id, self.full_name, self.emails)

    def test_matrix_nio_person(self):
        self.assertEqual(str(self.person1), self.person_id)

    def test_matrix_nio_person_id(self):
        identifier = matrix_nio.MatrixNioIdentifier("12345")
        self.assertEqual(self.person1, identifier)

    def test_matrix_nio_person_equality(self):
        person2 = matrix_nio.MatrixNioPerson(12345, "Not Charles de Gaulle", [])
        self.assertEqual(self.person1, person2)

    def test_matrix_nio_person_inequality(self):
        person2 = matrix_nio.MatrixNioPerson(54321, self.full_name, self.emails)
        self.assertNotEqual(self.person1, person2)

    def test_matrix_nio_person_acls(self):
        acls = "charles.degaulle@elysee.fr,charles@colombay.fr"
        self.assertEqual(self.person1.aclattr, acls)

    def test_matrix_nio_person_emails(self):
        emails = ["charles@colombay.fr", "charles.degaulle@elysee.fr"]
        self.assertEqual(self.person1.emails, emails)


class TestMatrixNioRoom(TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        self.client.rooms = {"test_room": "empty_room", "other_test_room": "also_empty_room"}

        self.room_id = "test_room"
        self.subject = "test_room"
        self.room1 = matrix_nio.MatrixNioRoom(self.room_id, self.subject, client=self.client)

    def test_matrix_nio_room(self):
        self.assertEqual(str(self.room1), self.room_id)


class TestMatrixNioRoomOccupant(TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.client = nio.AsyncClient("test.matrix.org", user="test_user", device_id="test_device")
        self.client.rooms = {"test_room": "empty_room", "other_test_room": "also_empty_room"}

        self.room_id = "test_room"
        self.subject = "test_room"
        self.room1 = matrix_nio.MatrixNioRoom(self.room_id, self.subject, client=self.client)

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
        room1 = matrix_nio.MatrixNioRoom(room_id1, subject1, client=self.client)
        self.assertEqual(self.room_occupant1.room, room1)


if __name__ == '__main__':
    unittest.main()
