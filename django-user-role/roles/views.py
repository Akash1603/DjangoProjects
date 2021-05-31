from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

import requests
# from oauth2_provider.contrib.rest_framework import (
#     OAuth2Authentication,
#     TokenMatchesOASRequirements,
# )
from django.utils.translation import gettext_lazy as _
from oauth2_provider.models import Application
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, _get_error_details, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from roles.models import Role, User
from users_role.settings import CACHE_TTL, HOSTNAME


class ErrorListField(serializers.ListField):
    error = serializers.DictField()


class BaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    errors = ErrorListField(required=False)
    data = serializers.JSONField(required=False)
    message = serializers.CharField()
    code = serializers.IntegerField()

    @staticmethod
    def success_response(result, status):
        return Response(
            BaseResponseSerializer(
                {
                    "success": True,
                    "data": result.data
                    if isinstance(result, serializers.ModelSerializer)
                    else result,
                    "code": status,
                    "message": constant["SuccessfullyCreated"]
                    if status == 201
                    else constant["SuccessfullyCompleted"],
                }
            ).data,
            status=status,
        )

    @staticmethod
    def error_response(error, status, message):
        if isinstance(error, Exception):
            return Response(
                BaseResponseSerializer(
                    {
                        "success": False,
                        "code": status,
                        "message": message,
                        "errors": [str(error)],
                        "data": {},
                    }
                ).data,
                status=status,
            )
        if isinstance(error, list):
            return Response(
                BaseResponseSerializer(
                    {
                        "success": False,
                        "message": message,
                        "data": {},
                        "code": status,
                        "errors": error,
                    }
                ).data,
                status=status,
            )
        return Response(
            BaseResponseSerializer(
                {
                    "success": False,
                    "message": message,
                    "data": {},
                    "code": status,
                    "errors": [error],
                }
            ).data,
            status=status,
        )


def validate_role(role):
    if not Role.objects.filter(name=role).exists():
        serializers.ValidationError({"role": "Invalid role."})


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(max_length=150)
    role = serializers.CharField(max_length=150)


class CreateUserView(APIView):
    """
    This class is used to create auth user and return auth token.
    """

    def post(self, request):
        try:
            serializer = CreateUserSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                email = serializer.validated_data["email"]
                username = serializer.validated_data["username"]
                password = serializer.validated_data["password"]
                try:
                    email['emai;l']
                except:
                    raise ValidationError({"success": True})
                    # return Response({"success":True})
                role = serializer.validated_data["role"]
                user = User.objects.create(
                    username=username,
                    email=email,
                )
                role = Role.objects.get(name=role)
                user.roles.add(role)
                user.is_active = True
                user.set_password(password)
                user.save()
                application = Application.objects.create(
                    user=user,
                    authorization_grant_type="password",
                    client_type="confidential",
                    name="user",
                )
                data = {
                    "username": user,
                    "password": password,
                    "grant_type": "password",
                    "client_id": application.client_id,
                    "client_secret": application.client_secret,
                }
                return Response(
                    requests.post(HOSTNAME + "o/token/", data=data).json(), status=201
                )
        except IntegrityError as e:
            raise ValidationError(
                {
                    "error": "{} not available,Please try with again.!!!".format(
                        e.args[0].split(".")[-1]
                    ).capitalize()
                }
            )

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request):
        return Response(User.objects.filter().values())


class RoleView(APIView):
    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [TokenMatchesOASRequirements]
    #
    # required_alternate_scopes = {
    #     "POST": [["create"]],
    #
    # }

    def post(self, request):
        try:
            role = request.data["role_type"]
            if not Role.objects.filter(name=role).exists():
                return Response(
                    {"role_name": Role.objects.create(name=role).name}, status=201
                )
            raise ValidationError({"error": "Roles type already exist."})
        except KeyError as e:
            raise ValidationError({e.args[0]: "This field is required."})
