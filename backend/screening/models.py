import uuid
from django.db import models


class ScreeningSession(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    class RespondentRole(models.TextChoices):
        MOTHER = "mother", "Mother"
        FATHER = "father", "Father"
        GUARDIAN = "guardian", "Guardian"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_name = models.CharField(max_length=255)
    child_first_name = models.CharField(max_length=255)
    child_age_months = models.PositiveIntegerField()
    child_sex = models.CharField(max_length=1, choices=Sex.choices)
    respondent_role = models.CharField(max_length=20, choices=RespondentRole.choices)
    main_concerns = models.JSONField(default=list, blank=True)
    address = models.CharField(max_length=500, blank=True, default="")
    postal_code = models.CharField(max_length=10, blank=True, default="")
    city = models.CharField(max_length=255, blank=True, default="")
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "screening_sessions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.child_first_name} ({self.child_age_months}m) - {self.created_at:%Y-%m-%d}"


class Question(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE_CHOICE = "single_choice", "Single Choice"
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        YES_NO = "yes_no", "Yes/No"
        SCALE = "scale", "Scale"

    class Domain(models.TextChoices):
        COMMUNICATION = "communication", "Communication"
        SOCIAL_INTERACTION = "social_interaction", "Social Interaction"
        BEHAVIOR = "behavior", "Repetitive Behaviors"
        SENSORY = "sensory", "Sensory Processing"
        MOTOR = "motor", "Motor Skills"
        AUTONOMY = "autonomy", "Autonomy"

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    text = models.TextField()
    description = models.TextField(blank=True, default="")
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    domain = models.CharField(max_length=30, choices=Domain.choices)
    score_weight = models.FloatField(default=1.0)
    age_min_months = models.PositiveIntegerField(default=0)
    age_max_months = models.PositiveIntegerField(default=144)
    is_active = models.BooleanField(default=True)
    trigger_flag = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        db_table = "questions"
        ordering = ["code"]

    def __str__(self):
        return f"[{self.code}] {self.name}"


class QuestionOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    is_red_flag = models.BooleanField(default=False)
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "question_options"
        ordering = ["order_index"]

    def __str__(self):
        return f"{self.label} (score={self.score})"


class QuestionBlock(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    age_min_months = models.PositiveIntegerField(default=0)
    age_max_months = models.PositiveIntegerField(default=144)
    is_core = models.BooleanField(default=True)
    questions = models.ManyToManyField(
        Question, through="BlockQuestion", related_name="blocks"
    )

    class Meta:
        db_table = "question_blocks"
        ordering = ["code"]

    def __str__(self):
        return f"[{self.code}] {self.name}"


class BlockQuestion(models.Model):
    block = models.ForeignKey(QuestionBlock, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "block_questions"
        ordering = ["order_index"]
        unique_together = [("block", "question")]


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ScreeningSession, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(
        QuestionOption, on_delete=models.SET_NULL, null=True, blank=True
    )
    raw_value = models.CharField(max_length=255, blank=True, default="")
    computed_score = models.FloatField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "answers"
        unique_together = [("session", "question")]

    def __str__(self):
        return f"Answer({self.session_id}, {self.question.code})"


class AnalysisResult(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MODERATE = "moderate", "Moderate"
        HIGH = "high", "High"
        VERY_HIGH = "very_high", "Very High"

    class RecommendationLevel(models.TextChoices):
        MONITOR = "monitor", "Monitor"
        PEDIATRIC = "pediatric_consultation", "Pediatric Consultation"
        SPECIALIST = "specialist_consultation", "Specialist Consultation"
        URGENT = "urgent_referral", "Urgent Referral"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(
        ScreeningSession, on_delete=models.CASCADE, related_name="result"
    )
    global_score = models.FloatField(default=0)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices)
    recommendation_level = models.CharField(
        max_length=30, choices=RecommendationLevel.choices
    )
    red_flags = models.JSONField(default=list)
    domain_scores = models.JSONField(default=dict)
    ai_summary = models.TextField(blank=True, default="")
    ai_confidence_notes = models.JSONField(default=list, blank=True)
    explanation_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analysis_results"

    def __str__(self):
        return f"Result({self.session_id}) - {self.risk_level}"


class Provider(models.Model):
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    lat = models.FloatField()
    lng = models.FloatField()
    phone = models.CharField(max_length=30, blank=True, default="")

    class Meta:
        db_table = "providers"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.specialty}"
