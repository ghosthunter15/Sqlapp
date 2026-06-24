import sqlite3
import argparse
import logging
import sys


# Initialize the logger
logging.basicConfig(filename='app.log',
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Log an error and exit gracefully
def log_error_and_exit(message):
    logging.error(message)
    sys.exit(1)


def connect_to_db():
    """Connect to SQLite database or create it."""
    try:
        connection = sqlite3.connect('hashes.db')
        return connection
    except sqlite3.Error as e:
        log_error_and_exit(f"Error connecting to database: {e}")


def create_table(connection):
    """Create the list table if it doesn't exist."""
    try:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS list (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            password TEXT NOT NULL,
                            hash TEXT NOT NULL UNIQUE
                        )''')
        connection.commit()
    except sqlite3.Error as e:
        log_error_and_exit(f"Error creating table: {e}")


def add_user(connection, password, hash_value):
    """Add a new user (password and hash) to the database."""
    try:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO list (password, hash) VALUES (?, ?)',
                       (password, hash_value))
        connection.commit()
        print(f"User with password '{password}' and hash '{hash_value}'\
                added successfully.")
    except sqlite3.Error as e:
        log_error_and_exit(f"Error adding user: {e}")


def list_users(connection, password=None, hash_value=None, lookup_id=False):
    """List all users, or look up a hash by password, password by hash,\
            or user ID by either."""
    try:
        cursor = connection.cursor()

        if password and lookup_id:
            # Look up the user ID for the specific password
            cursor.execute('SELECT id FROM list WHERE password = ?',
                           (password,))
            result = cursor.fetchone()
            if result:
                print(f"ID for password '{password}': {result[0]}")
            else:
                print(f"No ID found for password '{password}'.")
        elif hash_value and lookup_id:
            # Look up the user ID for the specific hash
            cursor.execute('SELECT id FROM list WHERE hash = ?', (hash_value,))
            result = cursor.fetchone()
            if result:
                print(f"ID for hash '{hash_value}': {result[0]}")
            else:
                print(f"No ID found for hash '{hash_value}'.")
        elif password:
            # Look up the hash for the specific password
            cursor.execute('SELECT hash FROM list WHERE password = ?',
                           (password,))
            result = cursor.fetchone()
            if result:
                print(f"Hash for password '{password}': {result[0]}")
            else:
                print(f"No hash found for password '{password}'.")
        elif hash_value:
            # Look up the password for the specific hash
            cursor.execute('SELECT password FROM list WHERE hash = ?',
                           (hash_value,))
            result = cursor.fetchone()
            if result:
                print(f"Password for hash '{hash_value}': {result[0]}")
            else:
                print(f"No password found for hash '{hash_value}'.")
        else:
            # List all users
            cursor.execute('SELECT * FROM list')
            users = cursor.fetchall()
            if users:
                for user in users:
                    print(f"ID: {user[0]}, Password: {user[1]},\
                            Hash: {user[2]}")
            else:
                print("No users found.")
    except sqlite3.Error as e:
        log_error_and_exit(f"Error listing users: {e}")


def update_user(connection, user_id, password, hash_value):
    """Update an existing user (password and hash) in the database."""
    try:
        cursor = connection.cursor()
        cursor.execute('UPDATE list SET password = ?, hash = ? WHERE id = ?',
                       (password, hash_value, user_id))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"User {user_id} updated successfully.")
        else:
            print(f"User {user_id} not found.")
    except sqlite3.Error as e:
        log_error_and_exit(f"Error updating user: {e}")


def delete_user(connection, user_id):
    """Delete a user from the database."""
    try:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM list WHERE id = ?', (user_id,))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"User {user_id} deleted successfully.")
        else:
            print(f"User {user_id} not found.")
    except sqlite3.Error as e:
        log_error_and_exit(f"Error deleting user: {e}")


def get_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="SQLite User Management App")

    subparsers = parser.add_subparsers(dest="command",
                                       help="Available commands")

    # Add a user
    add_parser = subparsers.add_parser("add", help="Add a new user")
    add_parser.add_argument("password", type=str, help="Password of the user")
    add_parser.add_argument("hash_value", type=str, help="Hash of the user")

    # List users, look up a hash by password,
    # look up password by hash, or find user ID
    list_parser = subparsers.add_parser("list",
                                        help="List all users,\
                                                look up hash/password,\
                                                or find user ID")
    list_parser.add_argument("-p", "--password", type=str,
                             help="Password to look up the hash or user ID")
    list_parser.add_argument("-H", "--hash_value", type=str,
                             help="Hash to look up the password or user ID")
    list_parser.add_argument("-l", "--lookup_id", action="store_true",
                             help="Flag to look up user ID by password or hash"
                             )

    # Update a user
    update_parser = subparsers.add_parser("update",
                                          help="Update an existing user")
    update_parser.add_argument("id", type=int, help="User ID")
    update_parser.add_argument("password", type=str,
                               help="New password of the user")
    update_parser.add_argument("hash_value", type=str,
                               help="New hash of the user")

    # Delete a user
    delete_parser = subparsers.add_parser("delete", help="Delete a user")
    delete_parser.add_argument("id", type=int, help="User ID to delete")

    return parser.parse_args()


def main():
    # Parse arguments
    args = get_args()

    # Connect to the database
    connection = connect_to_db()

    # Create the list table if it doesn't exist
    create_table(connection)

    # Perform operations based on the provided command
    if args.command == "add":
        add_user(connection, args.password, args.hash_value)
    elif args.command == "list":
        list_users(connection, args.password, args.hash_value, args.lookup_id)
    elif args.command == "update":
        update_user(connection, args.id, args.password, args.hash_value)
    elif args.command == "delete":
        delete_user(connection, args.id)
    else:
        print("Invalid command. Use --help for usage information.")

    # Close the database connection
    connection.close()


if __name__ == '__main__':
    main()
