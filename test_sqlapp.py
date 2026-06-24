import unittest
import sqlite3
import os
import sys
from unittest.mock import patch, MagicMock
from io import StringIO
from sqlapp import connect_to_db, create_table, add_user, list_users, \
        update_user, delete_user, get_args

# Add the parent directory to the sys.path so we can import sqlapp
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))


class TestSQLiteApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a temporary test database."""
        cls.test_db = 'test_hashes.db'
        cls.connection = sqlite3.connect(cls.test_db)
        create_table(cls.connection)

    @classmethod
    def tearDownClass(cls):
        """Tear down the test database."""
        cls.connection.close()
        os.remove(cls.test_db)

    def setUp(self):
        """Clear the table before every test."""
        self.cursor = self.connection.cursor()
        self.cursor.execute("DELETE FROM list")
        self.connection.commit()

    def test_add_user(self):
        """Test adding a user to the database."""
        add_user(self.connection, "testpassword", "testhash")
        self.cursor.execute("SELECT * FROM list WHERE password = ? \
                AND hash = ?", ("testpassword", "testhash"))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "testpassword")
        self.assertEqual(user[2], "testhash")

    def test_list_users(self):
        """Test listing users in the database."""
        add_user(self.connection, "testpassword1", "testhash1")
        add_user(self.connection, "testpassword2", "testhash2")
        self.cursor.execute("SELECT * FROM list")
        users = self.cursor.fetchall()
        self.assertEqual(len(users), 2)

    def test_lookup_hash_by_password(self):
        """Test looking up a hash by password."""
        add_user(self.connection, "testpassword", "testhash")
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            list_users(self.connection, password="testpassword")
            self.assertIn("Hash for password 'testpassword'",
                          mock_stdout.getvalue())

    def test_lookup_password_by_hash(self):
        """Test looking up a password by hash."""
        add_user(self.connection, "testpassword", "testhash")
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            list_users(self.connection, hash_value="testhash")
            self.assertIn("Password for hash 'testhash'",
                          mock_stdout.getvalue())

    def test_lookup_id_by_password(self):
        """Test looking up a user ID by password."""
        add_user(self.connection, "testpassword", "testhash")
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            list_users(self.connection, password="testpassword",
                       lookup_id=True)
            self.assertIn("ID for password 'testpassword'",
                          mock_stdout.getvalue())

    def test_lookup_id_by_hash(self):
        """Test looking up a user ID by hash."""
        add_user(self.connection, "testpassword", "testhash")
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            list_users(self.connection, hash_value="testhash", lookup_id=True)
            self.assertIn("ID for hash 'testhash'", mock_stdout.getvalue())

    def test_update_user(self):
        """Test updating a user's password and hash."""
        add_user(self.connection, "testpassword", "testhash")
        self.cursor.execute("SELECT id FROM list WHERE password = ?",
                            ("testpassword",))
        user_id = self.cursor.fetchone()[0]

        update_user(self.connection, user_id, "newpassword", "newhash")
        self.cursor.execute("SELECT * FROM list WHERE id = ?", (user_id,))
        user = self.cursor.fetchone()

        self.assertEqual(user[1], "newpassword")
        self.assertEqual(user[2], "newhash")

    def test_delete_user(self):
        """Test deleting a user from the database."""
        add_user(self.connection, "testpassword", "testhash")
        self.cursor.execute("SELECT id FROM list WHERE password = ?",
                            ("testpassword",))
        user_id = self.cursor.fetchone()[0]

        delete_user(self.connection, user_id)
        self.cursor.execute("SELECT * FROM list WHERE id = ?", (user_id,))
        user = self.cursor.fetchone()

        self.assertIsNone(user)

    @patch('sys.stdout', new_callable=StringIO)
    def test_help_command(self, mock_stdout):
        """Test that the --help command works and prints the help message."""
        test_args = ['your_app_file.py', '--help']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit):
                # argparse calls sys.exit() after showing help
                get_args()
        output = mock_stdout.getvalue()
        self.assertIn("usage:", output)
        self.assertIn("SQLite User Management App", output)


if __name__ == '__main__':
    unittest.main()
