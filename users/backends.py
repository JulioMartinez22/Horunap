# users/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class DebugModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"\n--- DEBUG AUTHENTICATE ---") # Marker
        print(f"Attempting login for: {username}") 

        try:
            user = UserModel._default_manager.get_by_natural_key(username)
            print(f"User '{username}' found in DB.")

            # --- THIS IS THE KEY CHECK ---
            is_password_valid = user.check_password(password) 
            print(f"Password check result for '{username}': {is_password_valid}")
            # --- END KEY CHECK ---

            if is_password_valid:
                if self.user_can_authenticate(user):
                    print(f"Authentication SUCCESSFUL for '{username}'.")
                    print(f"---------------------------\n")
                    return user
                else:
                    print(f"User '{username}' CANNOT authenticate (e.g., inactive).")
            else:
                print(f"Password check FAILED for '{username}'.")

        except UserModel.DoesNotExist:
            print(f"User '{username}' NOT FOUND in DB.")
            # Run the default password hasher once anyway to mitigate timing attacks
            UserModel().set_password(password) 

        print(f"Authentication FAILED for '{username}'.")
        print(f"---------------------------\n")
        return None # Explicitly return None on failure