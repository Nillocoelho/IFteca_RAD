from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class UserInactiveError(AuthenticationFailed):
    """Exceção específica para usuários inativos."""
    default_detail = "Sua conta está desativada. Entre em contato com a administração da biblioteca."
    default_code = "user_inactive"


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        UserModel = get_user_model()
        
        # Primeiro verifica se o usuário existe e está ativo
        user_obj = None
        try:
            user_obj = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            try:
                user_obj = UserModel.objects.get(username=email)
            except UserModel.DoesNotExist:
                pass
        
        # Se o usuário existe mas está inativo, retorna mensagem específica
        if user_obj and not user_obj.is_active:
            raise UserInactiveError()

        # Primeiro tenta autenticar assumindo que o username seja o email
        user = authenticate(username=email, password=password)

        # Se falhar, tenta localizar o usuario pelo campo email e autenticar com o username real
        if not user:
            try:
                user_obj = UserModel.objects.get(email=email)
                user = authenticate(username=user_obj.get_username(), password=password)
            except UserModel.DoesNotExist:
                user = None

        if not user:
            raise AuthenticationFailed("Credenciais invalidas")

        # Verifica novamente se está ativo (caso autenticação tenha sido bem-sucedida)
        if not user.is_active:
            raise UserInactiveError()

        data["user"] = user
        return data
