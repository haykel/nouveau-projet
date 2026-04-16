from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Health"],
    summary="Health check",
    description="Verifie que le serveur est operationnel.",
)
@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
