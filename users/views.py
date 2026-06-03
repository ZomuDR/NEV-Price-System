import time
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64

User = get_user_model()


@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])  # Token认证
@permission_classes([IsAuthenticated])  # 登录权限
def user_profile(request):
    """基于Token认证的用户信息接口"""
    try:
        # 从Token获取用户对象
        user = request.user

        # GET请求：返回用户信息
        if request.method == 'GET':
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,  # 适配前端字段
                "address": user.address,  # 适配前端字段
                "avatar": user.avatar.url if user.avatar else None
            })

        # PUT请求：更新用户信息
        elif request.method == 'PUT':
            data = request.data.copy()

            # 处理头像上传（base64格式）
            if 'avatar' in data and data['avatar']:
                avatar_data = data['avatar']

                # 验证base64图像数据
                if avatar_data.startswith('data:image'):
                    format, imgstr = avatar_data.split(';base64,')
                    ext = format.split('/')[-1]

                    # 解码并保存文件
                    data_bytes = base64.b64decode(imgstr)
                    file_name = f"avatar_{user.id}_{int(time.time())}.{ext}"
                    file_path = default_storage.save(
                        f'avatars/{file_name}',
                        ContentFile(data_bytes)
                    )
                    data['avatar'] = file_path

            # 手动更新用户字段（避免序列化器验证）
            update_fields = []
            if 'email' in data:
                user.email = data['email']
                update_fields.append('email')
            if 'phone' in data:
                user.phone = data['phone']
                update_fields.append('phone')
            if 'address' in data:
                user.address = data['address']
                update_fields.append('address')
            if 'avatar' in data:
                user.avatar = data['avatar']
                update_fields.append('avatar')

            # 保存更新
            if update_fields:
                user.save(update_fields=update_fields)

            return Response({
                "status": "success",
                "message": "用户信息更新成功"
            })
        return None

    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

    # 错误处理优化
    errors = {}
    field_error_map = {
        'username': {
            'unique': '用户名重复',
            'required': '用户名不能为空',
        },
        'email': {
            'unique': '邮箱已被注册',
            'required': '邮箱不能为空',
        },
        'phone': {
            'unique': '手机号已被注册',
            'required': '手机号不能为空',
        }
    }

    for field, field_errors in serializer.errors.items():
        # 获取该字段的第一个错误对象
        if isinstance(field_errors, list) and len(field_errors) > 0:
            first_error = field_errors[0]

            # 如果是字段相关错误
            if hasattr(first_error, 'code'):
                error_code = first_error.code
                # 从映射表中获取错误信息
                default_msg = str(first_error)
                errors[field] = field_error_map.get(field, {}).get(error_code, default_msg)
            else:
                errors[field] = str(first_error)
        else:
            errors[field] = str(field_errors)
    return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    # 检查用户是否存在（精确匹配）
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': '用户不存在，是否注册新用户？', 'code': 'user_not_found'},
            status=status.HTTP_404_NOT_FOUND
        )
    # 验证密码和用户状态
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        token, created = Token.objects.get_or_create(user=auth_user)
        return Response({
            'token': token.key,
            'user': {
                'username': user.username,
                'is_admin': user.is_staff,
            }
        })
    else:
        return Response(
            {'error': '用户名或密码错误，请重新登录！', 'code': 'invalid_credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """获取当前登录用户信息"""
    user = request.user
    return Response({
        'username': user.username,
    })

