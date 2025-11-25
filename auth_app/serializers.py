from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Primeiro tenta autenticar assumindo que o username seja o email
        user = authenticate(username=email, password=password)

        # Se falhar, tenta localizar o usuario pelo campo email e autenticar com o username real
        if not user:
            UserModel = get_user_model()
            try:
                user_obj = UserModel.objects.get(email=email)
                user = authenticate(username=user_obj.get_username(), password=password)
            except UserModel.DoesNotExist:
                user = None

        if not user:
            raise AuthenticationFailed("Credenciais invalidas")

        data["user"] = user
        return data
