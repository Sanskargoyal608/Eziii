from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from core.models import Student

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class to tell simplejwt to use our
    Student model instead of the default User model.
    """
    def get_user(self, validated_token):
        """
        Overrides the default get_user method.
        """
        try:
            # The USER_ID_FIELD in settings tells simplejwt to use 'student_id'
            # as the key in the token payload.
            user_id = validated_token[settings.SIMPLE_JWT['USER_ID_CLAIM']]
        except KeyError:
            from rest_framework_simplejwt.exceptions import InvalidToken
            raise InvalidToken("Token contained no recognizable user identification")

        try:
            student = Student.objects.get(student_id=user_id)
        except Student.DoesNotExist:
            from django.contrib.auth.models import AnonymousUser
            print(f"Authentication Failed: Student with id {user_id} not found.")
            return AnonymousUser() # Or raise an exception

        return student
