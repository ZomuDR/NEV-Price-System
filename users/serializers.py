from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        error_messages={
            'required': '密码不能为空',
            'blank': '密码不能为空'
        }
    )

    username = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': '用户名不能为空',
            'blank': '用户名不能为空',
        }
    )

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())],
        error_messages={
            'required': '邮箱不能为空',
            'blank': '邮箱不能为空',
        }
    )

    phone = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())],
        error_messages={
            'required': '手机号不能为空',
            'blank': '手机号不能为空'
        }
    )


    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address','password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance