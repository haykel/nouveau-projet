from rest_framework import status, serializers as drf_serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer

from .models import (
    ScreeningSession,
    QuestionBlock,
    Question,
    QuestionOption,
    Answer,
    AnalysisResult,
)
from .serializers import (
    SessionCreateSerializer,
    SessionSerializer,
    BlockQuestionsSerializer,
    AnswerBulkSerializer,
    AnalysisResultSerializer,
    ProviderSerializer,
)
from .services import ResultComposerService, ProviderMatcherService


@extend_schema(
    tags=["Sessions"],
    summary="Creer une session de depistage",
    description=(
        "Cree une nouvelle session de depistage pour un enfant. "
        "Les informations du parent, de l'enfant et la localisation sont enregistrees."
    ),
    request=SessionCreateSerializer,
    responses={201: SessionSerializer},
)
@api_view(["POST"])
def create_session(request):
    serializer = SessionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save()
    return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Sessions"],
    summary="Recuperer une session",
    description="Retourne les details d'une session de depistage existante.",
    responses={200: SessionSerializer, 404: None},
)
@api_view(["GET"])
def get_session(request, session_id):
    try:
        session = ScreeningSession.objects.get(pk=session_id)
    except ScreeningSession.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(SessionSerializer(session).data)


@extend_schema(
    tags=["Questionnaire"],
    summary="Recuperer les questions adaptees a l'age",
    description=(
        "Retourne les blocs de questions filtres selon l'age de l'enfant "
        "enregistre dans la session. Chaque question inclut ses options de reponse."
    ),
    responses={
        200: inline_serializer(
            name="QuestionsResponse",
            fields={
                "blocks": BlockQuestionsSerializer(many=True),
            },
        ),
        404: None,
    },
)
@api_view(["GET"])
def get_questions(request, session_id):
    try:
        session = ScreeningSession.objects.get(pk=session_id)
    except ScreeningSession.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )

    age = session.child_age_months
    blocks = QuestionBlock.objects.filter(
        age_min_months__lte=age, age_max_months__gte=age
    )
    serializer = BlockQuestionsSerializer(
        blocks, many=True, context={"child_age_months": age}
    )
    return Response({"blocks": serializer.data})


@extend_schema(
    tags=["Answers"],
    summary="Soumettre les reponses",
    description=(
        "Enregistre les reponses du parent pour la session donnee. "
        "Le score de chaque reponse est calcule automatiquement a partir de l'option selectionnee."
    ),
    request=AnswerBulkSerializer,
    responses={
        201: inline_serializer(
            name="AnswerSubmitResponse",
            fields={
                "submitted": drf_serializers.IntegerField(),
                "answer_ids": drf_serializers.ListField(child=drf_serializers.CharField()),
            },
        ),
        404: None,
    },
)
@api_view(["POST"])
def submit_answers(request, session_id):
    try:
        session = ScreeningSession.objects.get(pk=session_id)
    except ScreeningSession.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = AnswerBulkSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    created = []
    for answer_data in serializer.validated_data["answers"]:
        question = Question.objects.get(pk=answer_data["question_id"])
        selected_option = None
        computed_score = 0

        option_id = answer_data.get("selected_option_id")
        if option_id:
            selected_option = QuestionOption.objects.get(pk=option_id)
            computed_score = selected_option.score

        answer, _ = Answer.objects.update_or_create(
            session=session,
            question=question,
            defaults={
                "selected_option": selected_option,
                "raw_value": answer_data.get("raw_value", ""),
                "computed_score": computed_score,
            },
        )
        created.append(str(answer.id))

    return Response(
        {"submitted": len(created), "answer_ids": created},
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    tags=["Analysis"],
    summary="Lancer l'analyse complete",
    description=(
        "Declenche le pipeline d'analyse a 3 couches :\n\n"
        "1. **Moteur de regles** : scoring par domaine, detection des red flags, recommandation\n"
        "2. **Interpretation IA** : resume narratif structure (Claude API)\n"
        "3. **Validation de securite** : blocage du langage diagnostique\n\n"
        "Retourne le resultat complet avec les professionnels de sante a proximite."
    ),
    request=None,
    responses={200: AnalysisResultSerializer, 400: None, 404: None},
)
@api_view(["POST"])
def analyze_session(request, session_id):
    try:
        session = ScreeningSession.objects.get(pk=session_id)
    except ScreeningSession.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )

    answer_count = Answer.objects.filter(session=session).count()
    if answer_count == 0:
        return Response(
            {"error": "No answers submitted for this session"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    composer = ResultComposerService(session)
    result, providers = composer.analyze()

    serializer = AnalysisResultSerializer(
        result, context={"nearby_providers": providers}
    )
    return Response(serializer.data)


@extend_schema(
    tags=["Analysis"],
    summary="Recuperer les resultats d'analyse",
    description=(
        "Retourne les resultats d'une analyse deja effectuee, "
        "incluant les scores par domaine, les red flags, le resume IA valide, "
        "et les professionnels de sante a proximite."
    ),
    responses={200: AnalysisResultSerializer, 404: None},
)
@api_view(["GET"])
def get_results(request, session_id):
    try:
        session = ScreeningSession.objects.get(pk=session_id)
    except ScreeningSession.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )

    try:
        result = AnalysisResult.objects.get(session=session)
    except AnalysisResult.DoesNotExist:
        return Response(
            {"error": "No analysis results found. Run analysis first."},
            status=status.HTTP_404_NOT_FOUND,
        )

    providers = []
    if result.recommendation_level != "monitor":
        matcher = ProviderMatcherService()
        providers = matcher.find_nearby(session.lat, session.lng)

    serializer = AnalysisResultSerializer(
        result, context={"nearby_providers": providers}
    )
    return Response(serializer.data)


@extend_schema(
    tags=["Providers"],
    summary="Trouver les professionnels de sante a proximite",
    description=(
        "Recherche les professionnels de sante dans un rayon configurable "
        "autour des coordonnees fournies. Tries par pertinence (specialite) et distance."
    ),
    parameters=[
        OpenApiParameter(name="lat", type=float, required=True, description="Latitude"),
        OpenApiParameter(name="lng", type=float, required=True, description="Longitude"),
        OpenApiParameter(name="radius", type=float, required=False, description="Rayon de recherche en km (defaut: 30)"),
    ],
    responses={200: ProviderSerializer(many=True), 400: None},
)
@api_view(["GET"])
def nearby_providers(request):
    lat = request.query_params.get("lat")
    lng = request.query_params.get("lng")
    radius = request.query_params.get("radius")

    if not lat or not lng:
        return Response(
            {"error": "lat and lng parameters are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        lat = float(lat)
        lng = float(lng)
        radius = float(radius) if radius else None
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid lat, lng or radius values"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    matcher = ProviderMatcherService()
    providers = matcher.find_nearby(lat, lng, radius_km=radius)
    return Response(ProviderSerializer(providers, many=True).data)
