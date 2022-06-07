import json

from django.conf import settings
from jwcrypto import jwt, jwk
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import NotFound, AuthenticationFailed, PermissionDenied

from users.models import Users, Roles

key = jwk.JWK(**settings.SECRET_KEY_JWT)


def token_decode(request):
    try:
        access_token = request.headers.get("Authorization")
        access_token = jwt.JWT(key=key, jwt=access_token)
        access_token = jwt.JWT(key=key, jwt=access_token.claims)
        claims = json.loads(access_token.claims)
        user = Users.objects.get(email=claims["email"])
        return user, claims
    except Users.DoesNotExist as e:
        raise NotFound(detail="Token not valid")
    except Exception as e:
        raise AuthenticationFailed(detail="Token not valid")


class SafeJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        client = token_decode(request)
        return client


class CanModifyBooks(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.method == 'GET':
                return True
            else:
                user_role = Users.objects.get(id=request.user.id).role
                if user_role == Roles.ADMIN.value:
                    return True
                else:
                    return False

        except Users.DoesNotExist:
            raise PermissionDenied
