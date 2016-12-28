from test_plus.test import TestCase


class TestUser(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            'testuser'  # This is the default username for self.make_user()
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.user.get_absolute_url(),
            '/users/testuser/'
        )

    def test_short_name(self):
        self.assertEqual(self.user.short_name, 'John D.')
        self.user.last_name = ''
        self.assertEqual(self.user.short_name, 'John')
        self.user.first_name = ''
        self.assertEqual(self.user.short_name, 'testuser')
