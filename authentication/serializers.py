from rest_framework import serializers

from .models import Role, Roles, User


class RoleSerializer(serializers.ModelSerializer):
    """Shows role name and title"""
    class Meta:
        """Model data"""
        model = Role
        fields = ["name", "title"]
        read_only_fields = ["name", "title"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for regular users"""
    password_confirm = serializers.CharField(write_only=True)
    role = RoleSerializer(default=Role.objects.get(id=Roles.USER))

    class Meta:
        """Users can view their data but cannot ban or change roles"""
        model = User
        fields = ["email", "username", "password",
                  "password_confirm", "blocked_until", "role"]
        read_only_fields = ["blocked_until", "role"]
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

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        if password := validated_data.get("password"):
            if password != validated_data.get("password_confirm"):
                raise serializers.ValidationError({
                    "password_confirm": ["Passwords do not match."]
                })
            instance.set_password(password)
        instance.save()
        return instance


class ModeratorSerializer(UserSerializer):
    """Serializer for moderators"""
    class Meta(UserSerializer.Meta):
        """Moderators can set ban status but not roles"""
        read_only_fields = ["role"]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.blocked_until = validated_data.get(
            "blocked_until", instance.blocked_until)
        instance.save()
        return instance


class AdminSerializer(ModeratorSerializer):
    """Serializer for admins. Includes a workaround for role setting"""
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta(ModeratorSerializer.Meta):
        """All fields can be changed"""
        fields = ["email", "username", "password",
                  "password_confirm", "blocked_until", "role"]
        read_only_fields = None

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.role = validated_data.get("role", instance.role)
        instance.save()
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["role"] = RoleSerializer(instance.role).data
        return response


def select_serializer(role):
    if role == Roles.ADMIN:
        return AdminSerializer
    elif role == Roles.MODERATOR:
        return ModeratorSerializer
    return UserSerializer
