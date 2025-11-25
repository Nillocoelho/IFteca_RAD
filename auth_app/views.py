from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer


class LoginView(APIView):

    # Permite GET apenas para mostrar o formulario no navegador
    def get(self, request):
        return Response({"detail": "Use POST para fazer login."})

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "email": user.email,
            }
        )


def login_page(request):
    return render(request, "auth_app/login.html")
