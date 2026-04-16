from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from app.authentication import KeycloakAuthentication, require_role


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def hello(request):
    username = request.user.get("preferred_username", "anonymous")
    return Response({"message": f"Hello World, {username}!"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health(request):
    return Response({"status": "ok"})
