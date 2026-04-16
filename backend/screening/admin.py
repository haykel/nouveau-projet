from django.contrib import admin
from .models import (
    ScreeningSession,
    Question,
    QuestionOption,
    QuestionBlock,
    BlockQuestion,
    Answer,
    AnalysisResult,
    Provider,
)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "domain", "question_type", "age_min_months", "age_max_months", "is_active"]
    list_filter = ["domain", "question_type", "is_active"]
    search_fields = ["code", "name", "text"]
    inlines = [QuestionOptionInline]


class BlockQuestionInline(admin.TabularInline):
    model = BlockQuestion
    extra = 1


@admin.register(QuestionBlock)
class QuestionBlockAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "age_min_months", "age_max_months", "is_core"]
    inlines = [BlockQuestionInline]


@admin.register(ScreeningSession)
class ScreeningSessionAdmin(admin.ModelAdmin):
    list_display = ["child_first_name", "child_age_months", "child_sex", "city", "created_at"]
    list_filter = ["child_sex", "created_at"]
    search_fields = ["child_first_name", "parent_name", "city"]
    readonly_fields = ["id", "created_at"]


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ["session", "risk_level", "recommendation_level", "global_score", "created_at"]
    list_filter = ["risk_level", "recommendation_level"]
    readonly_fields = ["id", "created_at"]


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ["name", "specialty", "city", "phone"]
    list_filter = ["specialty", "city"]
    search_fields = ["name", "specialty", "city"]
