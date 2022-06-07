import time

import bcrypt
from django.conf import settings
from django.core.exceptions import BadRequest
from drf_yasg.utils import swagger_auto_schema
from jwcrypto import jwk, jwt
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Users
from users.serializers import UserSerializer, LoginSerializer

key = jwk.JWK(**settings.SECRET_KEY_JWT)


def generate_token(user):
    access_token = jwt.JWT(header={"alg": settings.JWT_ALG},
                           claims={"email": user.email, "login_time": time.time(),
                                   "role": user.role
                                   },
                           default_claims={
                               "exp": round(time.time()) + settings.ACCESS_VALID_SECONDS})

    access_token.make_signed_token(key)

    access_token = access_token.serialize()

    encrypted_access_token = jwt.JWT(header=settings.ENCRYPT_ALG_DATA, claims=access_token)

    encrypted_access_token.make_encrypted_token(key)

    encrypted_access_token = encrypted_access_token.serialize()

    return {"access_token": encrypted_access_token}


def create_hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()


def check_password(request_password, hash_password):
    if bcrypt.checkpw(request_password.encode("utf8"), hash_password.encode("utf8")):
        return True
    else:
        return False


def check_user_exist(request):
    if "email" in request.data and Users.objects.filter(email__iexact=request.data["email"]):
        raise BadRequest("User with given email already exists.")


class UserView(APIView):
    @staticmethod
    @swagger_auto_schema(
        operation_description="User Registration",
        request_body=UserSerializer,
        responses={201: "User registered successfully.",
                   400: "User Registration done successfully." + " | " + "Email Already exists.",
                   500: "There is some internal server error."})
    def post(request):
        try:
            check_user_exist(request)
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data.update({
                    "password": create_hash_password(request.data["password"])
                })
                serializer.save()

                return Response({"message": "User Registration done successfully."}, status.HTTP_201_CREATED)

            else:
                raise BadRequest("All the required information is not present")

        except BadRequest as e:
            raise BadRequest(e)
        except Exception as e:
            raise Exception(e)


class Login(APIView):
    @staticmethod
    @swagger_auto_schema(request_body=LoginSerializer,
                         responses={200: "User authenticated successfully.",
                                    400: "Email or password not provided",
                                    401: "Incorrect Credentials.",
                                    404: "No user exists with given email.",
                                    500: "There is some internal server error."},
                         operation_description="User Authentication")
    def post(request):
        try:
            login_serializer = LoginSerializer(data=request.data)
            if login_serializer.is_valid():
                user = Users.objects.get(email=request.data["email"])

                if check_password(request.data["password"], user.password):
                    return Response(generate_token(user), status.HTTP_200_OK)
                else:
                    raise AuthenticationFailed(detail="Incorrect Credentials.", code=2401)
            else:
                raise BadRequest("Email or password not provided.")

        except Users.DoesNotExist as e:
            raise AuthenticationFailed(detail="No user exists with given email.")
        except AuthenticationFailed as e:
            raise AuthenticationFailed(e)
        except BadRequest as e:
            raise BadRequest(e)
        except Exception as e:
            raise Exception(e)
