from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
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
        # Autentica na sessao para que rotas protegidas por login_required funcionem
        login(request, user)

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


def logout_view(request):
    """
    Encerra a sessao (logout) e redireciona para a tela de login. Se a chamada
    esperar JSON (ex.: fetch na UI), responde com JSON ao inves de redirecionar.
    """
    next_url = request.GET.get("next") or reverse("login_page")

    if request.user.is_authenticated:
        logout(request)

    wants_json = "application/json" in request.headers.get("Accept", "")
    if wants_json:
        return Response({"detail": "Logout realizado com sucesso.", "next": next_url})

    return redirect(next_url)
