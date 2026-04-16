from rest_framework import serializers
from .models import (
    ScreeningSession,
    Question,
    QuestionOption,
    QuestionBlock,
    Answer,
    AnalysisResult,
    Provider,
)


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningSession
        fields = [
            "parent_name",
            "child_first_name",
            "child_age_months",
            "child_sex",
            "respondent_role",
            "main_concerns",
            "address",
            "postal_code",
            "city",
            "lat",
            "lng",
        ]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningSession
        fields = "__all__"


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "label", "value", "score", "is_red_flag", "order_index"]


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "code",
            "name",
            "text",
            "description",
            "question_type",
            "domain",
            "score_weight",
            "age_min_months",
            "age_max_months",
            "trigger_flag",
            "options",
        ]


class BlockQuestionsSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = QuestionBlock
        fields = ["id", "code", "name", "is_core", "questions"]

    def get_questions(self, obj):
        age = self.context.get("child_age_months")
        qs = obj.questions.filter(is_active=True)
        if age is not None:
            qs = qs.filter(age_min_months__lte=age, age_max_months__gte=age)
        qs = qs.order_by("blockquestion__order_index")
        return QuestionSerializer(qs, many=True).data


class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField(required=False, allow_null=True)
    raw_value = serializers.CharField(required=False, allow_blank=True, default="")


class AnswerBulkSerializer(serializers.Serializer):
    answers = AnswerSubmitSerializer(many=True)


class ProviderSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Provider
        fields = [
            "id",
            "name",
            "specialty",
            "address",
            "city",
            "postal_code",
            "phone",
            "distance_km",
        ]


class DomainScoreSerializer(serializers.Serializer):
    score = serializers.FloatField()
    max_score = serializers.FloatField()
    percentage = serializers.FloatField()


class AnalysisResultSerializer(serializers.ModelSerializer):
    nearby_providers = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisResult
        fields = [
            "id",
            "session_id",
            "global_score",
            "risk_level",
            "recommendation_level",
            "red_flags",
            "domain_scores",
            "ai_summary",
            "ai_confidence_notes",
            "explanation_json",
            "created_at",
            "nearby_providers",
        ]

    def get_nearby_providers(self, obj):
        providers = self.context.get("nearby_providers", [])
        return ProviderSerializer(providers, many=True).data
