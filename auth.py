import bcrypt
import os

USER_DATA_FILE = "users.txt"


def hash_password(plain_text_password):
    # Encode the password to bytes (bcrypt requires byte strings)
    password_bytes = plain_text_password.encode('utf-8')

    # Generate a salt using bcrypt.gensalt()
    salt = bcrypt.gensalt()

    # Hash the password using bcrypt.hashpw()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # Decode the hash back to a string to store in a text file
    return hashed_password.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    # Encode both the plaintext password and stored hash to bytes
    password_bytes = plain_text_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    # bcrypt.checkpw handles extracting the salt and comparing
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


def register_user(username, password):
    # Check if the username already exists
    exists = user_exists(username)

    if exists == True:
        print(f"Error: Username '{username}' already exists.")
        return False

    """ Register a new user """
    #  Hash the password
    hashed_password = hash_password(password)

    # Append the new user to the file
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username}, {hashed_password}\n")

    # Format: username,hashed_password
    print(f"Success: User '{username}' registered successfully!")

    return True


def user_exists(username):
    # Handle the case where the file doesn't exist yet
    if not os.path.exists(USER_DATA_FILE):
        return False

    # File exists, check for the username
    with open(USER_DATA_FILE, 'r') as f:
        for line in f.readlines():
            user_parts = line.strip().split(',', 1)

            # Check if line is properly formatted and username matches
            if len(user_parts) == 2 and username == user_parts[0].strip():
                return True

    return False


def login_user(username, password):
    # Handle the case where no users are registered yet
    if not os.path.exists(USER_DATA_FILE):
        return False

    """ Log in an existing user """
    with open(USER_DATA_FILE, 'r') as f:

        # Search for the username in the file
        for line in f.readlines():
            user, hash = line.strip().split(',', 1)

            # XXX To remove any leading whitespace, i.e. \n
            user = user.strip()
            hash = hash.strip()

            # If username matches, verify the password
            if user == username:
                return verify_password(password, hash)

    # If we reach here, the username was not found
    return False


def validate_username(username):
    # Checks if username is between 3 and 20 characters long
    if not (3 <= len(username) <= 20):
        return False, "Username must be between 3 and 20 characters."

    punct = ['\\', '/', ':', '*', '?', '\"', '<', '>', '|']

    # Checks if username contains the ff. punctuation
    for char in username:
        if char in punct:
            return False, "Username cannot contain the following symbols: \\/:*?\"<>|"

    return True, "Valid username"


def validate_password(password):
    # Must be between 6 and 50 characters long
    if not (6 <= len(password) <= 50):
        return False, "Password must be between 6 and 50 characters long."

    return True, "Password is valid"


def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)


def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            register_user(username, password)

        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            if login_user(username, password):
                print(f"\nSuccess: Welcome, {username}!")

                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")

            elif user_exists(username) == False:
                print("Error: Username not found.")
                input("\nPress Enter to return to main menu...")

            else:
                print("Error: Invalid password.")
                input("\nPress Enter to return to main menu...")

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
