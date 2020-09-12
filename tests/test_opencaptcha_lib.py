import unittest
import time

from opencaptcha_lib import check_ip_in_lists, DBconnector, token_length


class OpenCaptchaLibTest(unittest.TestCase):

    def setUp(self):
        self.db = DBconnector()

    def test_db_methods(self):

        self.db.delete('test_key')

        self.db.set_value('test_key', 'test_value')
        self.assertEqual(self.db.get_value('test_key'), 'test_value')
        self.db.delete('test_key')
        self.assertEqual(self.db.get_value('test_key'), None)

        self.db.set_dict('test_key', {'test_value': '1', 'test_value2': 2})
        self.assertEqual(self.db.get_dict('test_key'), {'test_value': '1', 'test_value2': 2})
        self.db.delete('test_key')
        self.assertEqual(self.db.get_value('test_key'), None)

        self.db.set_set('test_key', set(['1', '2']))
        self.db.set_set('test_key_updated', 1)
        self.assertTrue(self.db.set_exists('test_key', '1'))
        self.assertFalse(self.db.set_exists('test_key', '3'))
        self.db.delete('test_key')
        self.db.delete('test_key_updated')
        self.assertEqual(self.db.get_value('test_key'), None)

        token_key = 'test_key' + 'a' * (token_length - len('test_key'))
        self.db.set_dict(token_key, {'expires': 1}, expire=1)
        time.sleep(1.1)
        self.db.delete_old_keys()
        self.assertEqual(self.db.get_value(token_key), None)

    def test_check_ip_in_lists(self):

        try:
            penalty_added = check_ip_in_lists('100.64.0.0', self.db, {'tor_penalty': 0, 'vpn_penalty': 0, 'blacklist_penalty': 10})
        except BaseException:
            raise ValueError('blacklist ips not populated, run "update_ip_lists(force=True)" in server.py first')

        self.assertEqual(penalty_added, 10)

    def tearDown(self):
        self.db.close()


if __name__ == '__main__':
    unittest.main()
