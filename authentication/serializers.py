from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password_confirm"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data["password"]
        password_confirm = validated_data.pop("password_confirm")
        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": ["Passwords do not match."]
            })
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ModeratorSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["email", "username", "password",
                  "password_confirm", "blocked_until"]


class AdminSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["email", "username", "password",
                  "password_confirm", "blocked_until", "role"]
