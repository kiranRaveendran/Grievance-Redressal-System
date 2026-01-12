from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        email = attrs.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                {"email": "A user with that email already exists."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        validated_data['email'] = validated_data.get('email', '').lower()

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

       
        if hasattr(user, 'role'):
            user.role = 'citizen'
            user.is_active = True
            user.save(update_fields=['role', 'is_active'])

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'role',
        )
        read_only_fields = ('id', 'date_joined')


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for admin-created users.
    Admin can set role; password is mandatory.
    """
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'password',
        )
        read_only_fields = ('id',)

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)

        if getattr(user, 'role', None) == 'admin':
            user.is_staff = True
        else:
            user.is_staff = False

        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if getattr(instance, 'role', None) == 'admin':
            instance.is_staff = True
        else:
            instance.is_staff = False

        instance.save()
        return instance
