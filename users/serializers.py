import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User


PHONE_FORMAT = r'^\+380\d{9}$'
USERNAME_FORMAT = r'(?i)\b[a-z]+\b'
PASSWORD_FORMAT = r'^[A-Z]+?[\w@#$%^&+=]'


PHONE_FORMAT_ERROR = "Phone number must be in the entered in the UA country format: '+380999999999'"
USERNAME_FORMAT_ERROR = 'field must contain only letters'
DUPLICATE_EMAIL_ERROR = 'Email is already in use'
PASSWORD_LENGTH_ERROR = 'Password length has to be on range 6-30 symbol'
PASSWORD_FORMAT_ERROR = 'Password must start with uppercase letter. Can contain letters, ' \
                        'numbers and special symbols - @#$%^&+=_'


class UserSerializer(serializers.ModelSerializer):
    """
        User Serializer for create/update users.
    """
    first_name = serializers.RegexField(USERNAME_FORMAT, max_length=25,
                                        error_messages={'invalid': 'Firs name ' + USERNAME_FORMAT_ERROR})

    last_name = serializers.RegexField(USERNAME_FORMAT, max_length=25, required=False,
                                       error_messages={'invalid': 'Last name ' + USERNAME_FORMAT_ERROR})

    email = serializers.EmailField(max_length=30, validators=[
        UniqueValidator(queryset=User.objects.all(), message=DUPLICATE_EMAIL_ERROR)
    ])

    phone = serializers.RegexField(PHONE_FORMAT, required=False, error_messages={'invalid': PHONE_FORMAT_ERROR})

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, password):
        if not re.match(PASSWORD_FORMAT, password):
            raise serializers.ValidationError(PASSWORD_FORMAT_ERROR)
        if len(password) not in range(6, 30):
            raise serializers.ValidationError(PASSWORD_LENGTH_ERROR)

        return password

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # Encrypt new password if him was in the parameter body
        if validated_data.get('password') is not None:
            validated_data['password'] = make_password(validated_data['password'])

        # Update User data or get old data
        for field in UserSerializer.Meta.fields:
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))

        instance.save()
        return instance


class LoginSerializer(serializers.ModelSerializer):
    """
        User Serializer for token authentication.
    """
    email = serializers.EmailField(max_length=30)

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
