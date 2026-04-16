from django.core.management.base import BaseCommand
from screening.models import Question, QuestionOption, QuestionBlock, BlockQuestion


QUESTIONS_DATA = [
    # --- Questions for older children (72-144 months / 6-12 years) ---
    {
        "code": "COM_04",
        "name": "Conversation reciproque",
        "text": "Votre enfant peut-il maintenir une conversation en faisant des allers-retours (poser des questions, repondre, relancer) ?",
        "domain": "communication",
        "question_type": "single_choice",
        "age_min_months": 48,
        "age_max_months": 144,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Regulierement", "value": "regularly", "score": 0, "is_red_flag": False},
            {"label": "Parfois", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Jamais", "value": "never", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "COM_05",
        "name": "Comprehension du langage figure",
        "text": "Votre enfant comprend-il les expressions figurees, l'humour ou le sarcasme ?",
        "domain": "communication",
        "question_type": "single_choice",
        "age_min_months": 72,
        "age_max_months": 144,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Oui, facilement", "value": "easily", "score": 0, "is_red_flag": False},
            {"label": "Parfois, avec des difficultes", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Non, il prend tout au premier degre", "value": "never", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "SOC_06",
        "name": "Relations amicales",
        "text": "Votre enfant a-t-il des amis proches et entretient-il des relations amicales stables ?",
        "domain": "social_interaction",
        "question_type": "single_choice",
        "age_min_months": 48,
        "age_max_months": 144,
        "score_weight": 1.5,
        "trigger_flag": "",
        "options": [
            {"label": "Oui, plusieurs amis proches", "value": "several", "score": 0, "is_red_flag": False},
            {"label": "Un ou deux amis", "value": "few", "score": 1, "is_red_flag": False},
            {"label": "Des difficultes a se faire des amis", "value": "difficulty", "score": 2, "is_red_flag": False},
            {"label": "Aucun ami proche", "value": "none", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "SOC_07",
        "name": "Comprehension des emotions",
        "text": "Votre enfant comprend-il les emotions des autres (quand quelqu'un est triste, en colere, content) ?",
        "domain": "social_interaction",
        "question_type": "single_choice",
        "age_min_months": 48,
        "age_max_months": 144,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Oui, facilement", "value": "easily", "score": 0, "is_red_flag": False},
            {"label": "Parfois", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Non, il ne semble pas les percevoir", "value": "never", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "SOC_08",
        "name": "Comportement en groupe",
        "text": "Votre enfant participe-t-il aux activites de groupe (jeux collectifs, travail en equipe a l'ecole) ?",
        "domain": "social_interaction",
        "question_type": "single_choice",
        "age_min_months": 72,
        "age_max_months": 144,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Participe activement", "value": "active", "score": 0, "is_red_flag": False},
            {"label": "Participe si encourage", "value": "with_help", "score": 1, "is_red_flag": False},
            {"label": "Reste souvent en retrait", "value": "withdrawn", "score": 2, "is_red_flag": False},
            {"label": "Refuse ou evite les activites de groupe", "value": "refuses", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "BEH_03",
        "name": "Interets restreints",
        "text": "Votre enfant a-t-il des interets tres intenses et limites a un ou deux sujets specifiques ?",
        "domain": "behavior",
        "question_type": "single_choice",
        "age_min_months": 48,
        "age_max_months": 144,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Non, interets varies", "value": "varied", "score": 0, "is_red_flag": False},
            {"label": "Quelques interets predominants mais pas exclusifs", "value": "some", "score": 1, "is_red_flag": False},
            {"label": "Un ou deux interets tres intenses", "value": "intense", "score": 2, "is_red_flag": False},
            {"label": "Un seul interet qui occupe la majorite de son temps", "value": "exclusive", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "BEH_04",
        "name": "Adaptation au changement",
        "text": "Comment votre enfant reagit-il face aux changements imprevus (annulation d'une activite, changement de programme) ?",
        "domain": "behavior",
        "question_type": "single_choice",
        "age_min_months": 72,
        "age_max_months": 144,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "S'adapte facilement", "value": "easily", "score": 0, "is_red_flag": False},
            {"label": "Besoin d'un peu de temps", "value": "needs_time", "score": 1, "is_red_flag": False},
            {"label": "Forte frustration ou anxiete", "value": "frustrated", "score": 2, "is_red_flag": False},
            {"label": "Crises intenses (colere, pleurs prolonges)", "value": "meltdown", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "SEN_03",
        "name": "Surcharge sensorielle",
        "text": "Votre enfant est-il submerge dans les environnements bruyants ou tres stimulants (centres commerciaux, cantines, fetes) ?",
        "domain": "sensory",
        "question_type": "single_choice",
        "age_min_months": 48,
        "age_max_months": 144,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Non, a l'aise", "value": "comfortable", "score": 0, "is_red_flag": False},
            {"label": "Legerement incommode", "value": "slight", "score": 1, "is_red_flag": False},
            {"label": "Souvent submerge", "value": "often", "score": 2, "is_red_flag": False},
            {"label": "Evite completement ces situations", "value": "avoids", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "COM_01",
        "name": "Mots isoles",
        "text": "Votre enfant utilise-t-il des mots isoles pour demander ce qu'il veut ?",
        "domain": "communication",
        "question_type": "single_choice",
        "age_min_months": 12,
        "age_max_months": 48,
        "score_weight": 1.5,
        "trigger_flag": "no_single_words_at_24_months",
        "options": [
            {"label": "Regulierement", "value": "regularly", "score": 0, "is_red_flag": False},
            {"label": "Parfois", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Jamais", "value": "never", "score": 3, "is_red_flag": True},
        ],
    },
    {
        "code": "COM_02",
        "name": "Combinaison de mots",
        "text": "Votre enfant combine-t-il deux mots ou plus (ex: 'encore lait', 'papa parti') ?",
        "domain": "communication",
        "question_type": "single_choice",
        "age_min_months": 18,
        "age_max_months": 48,
        "score_weight": 1.0,
        "trigger_flag": "no_phrases_at_36_months",
        "options": [
            {"label": "Regulierement", "value": "regularly", "score": 0, "is_red_flag": False},
            {"label": "Parfois", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Jamais", "value": "never", "score": 3, "is_red_flag": True},
        ],
    },
    {
        "code": "COM_03",
        "name": "Regression langagiere",
        "text": "Votre enfant a-t-il perdu des mots ou des phrases qu'il utilisait auparavant ?",
        "domain": "communication",
        "question_type": "yes_no",
        "age_min_months": 12,
        "age_max_months": 72,
        "score_weight": 2.0,
        "trigger_flag": "language_regression",
        "options": [
            {"label": "Non", "value": "no", "score": 0, "is_red_flag": False},
            {"label": "Oui", "value": "yes", "score": 3, "is_red_flag": True},
        ],
    },
    {
        "code": "SOC_01",
        "name": "Reponse au prenom",
        "text": "Votre enfant reagit-il quand vous l'appelez par son prenom ?",
        "domain": "social_interaction",
        "question_type": "single_choice",
        "age_min_months": 9,
        "age_max_months": 72,
        "score_weight": 1.5,
        "trigger_flag": "no_response_to_name",
        "options": [
            {"label": "Toujours", "value": "always", "score": 0, "is_red_flag": False},
            {"label": "Souvent", "value": "often", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Jamais", "value": "never", "score": 3, "is_red_flag": True},
        ],
    },
    {
        "code": "SOC_02",
        "name": "Contact visuel",
        "text": "Votre enfant vous regarde-t-il dans les yeux lorsque vous lui parlez ?",
        "domain": "social_interaction",
        "question_type": "single_choice",
        "age_min_months": 6,
        "age_max_months": 72,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Regulierement", "value": "regularly", "score": 0, "is_red_flag": False},
            {"label": "Parfois", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Jamais", "value": "never", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "SOC_03",
        "name": "Pointage",
        "text": "Votre enfant pointe-t-il du doigt pour montrer quelque chose qui l'interesse ?",
        "domain": "social_interaction",
        "question_type": "single_choice",
        "age_min_months": 12,
        "age_max_months": 48,
        "score_weight": 1.5,
        "trigger_flag": "no_pointing",
        "options": [
            {"label": "Regulierement", "value": "regularly", "score": 0, "is_red_flag": False},
            {"label": "Parfois", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Jamais", "value": "never", "score": 3, "is_red_flag": True},
        ],
    },
    {
        "code": "SOC_04",
        "name": "Attention conjointe",
        "text": "Votre enfant suit-il votre regard quand vous pointez quelque chose ?",
        "domain": "social_interaction",
        "question_type": "single_choice",
        "age_min_months": 12,
        "age_max_months": 48,
        "score_weight": 1.0,
        "trigger_flag": "no_joint_attention",
        "options": [
            {"label": "Regulierement", "value": "regularly", "score": 0, "is_red_flag": False},
            {"label": "Parfois", "value": "sometimes", "score": 1, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 2, "is_red_flag": False},
            {"label": "Jamais", "value": "never", "score": 3, "is_red_flag": True},
        ],
    },
    {
        "code": "SOC_05",
        "name": "Regression sociale",
        "text": "Votre enfant a-t-il perdu de l'interet pour les interactions sociales qu'il avait auparavant ?",
        "domain": "social_interaction",
        "question_type": "yes_no",
        "age_min_months": 12,
        "age_max_months": 72,
        "score_weight": 2.0,
        "trigger_flag": "social_regression",
        "options": [
            {"label": "Non", "value": "no", "score": 0, "is_red_flag": False},
            {"label": "Oui", "value": "yes", "score": 3, "is_red_flag": True},
        ],
    },
    {
        "code": "BEH_01",
        "name": "Mouvements repetitifs",
        "text": "Votre enfant fait-il des mouvements repetitifs (battements de mains, balancements, tournoiements) ?",
        "domain": "behavior",
        "question_type": "single_choice",
        "age_min_months": 12,
        "age_max_months": 72,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Jamais", "value": "never", "score": 0, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 1, "is_red_flag": False},
            {"label": "Souvent", "value": "often", "score": 2, "is_red_flag": False},
            {"label": "Tres souvent", "value": "very_often", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "BEH_02",
        "name": "Routines rigides",
        "text": "Votre enfant reagit-il fortement aux changements dans ses routines ?",
        "domain": "behavior",
        "question_type": "single_choice",
        "age_min_months": 18,
        "age_max_months": 72,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Jamais", "value": "never", "score": 0, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 1, "is_red_flag": False},
            {"label": "Souvent", "value": "often", "score": 2, "is_red_flag": False},
            {"label": "Tres souvent", "value": "very_often", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "SEN_01",
        "name": "Sensibilite aux sons",
        "text": "Votre enfant couvre-t-il ses oreilles ou reagit-il fortement a certains sons ?",
        "domain": "sensory",
        "question_type": "single_choice",
        "age_min_months": 12,
        "age_max_months": 72,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Jamais", "value": "never", "score": 0, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 1, "is_red_flag": False},
            {"label": "Souvent", "value": "often", "score": 2, "is_red_flag": False},
            {"label": "Tres souvent", "value": "very_often", "score": 3, "is_red_flag": False},
        ],
    },
    {
        "code": "SEN_02",
        "name": "Sensibilite aux textures",
        "text": "Votre enfant evite-t-il certaines textures (vetements, aliments, surfaces) ?",
        "domain": "sensory",
        "question_type": "single_choice",
        "age_min_months": 12,
        "age_max_months": 72,
        "score_weight": 1.0,
        "trigger_flag": "",
        "options": [
            {"label": "Jamais", "value": "never", "score": 0, "is_red_flag": False},
            {"label": "Rarement", "value": "rarely", "score": 1, "is_red_flag": False},
            {"label": "Souvent", "value": "often", "score": 2, "is_red_flag": False},
            {"label": "Tres souvent", "value": "very_often", "score": 3, "is_red_flag": False},
        ],
    },
]

BLOCKS_DATA = [
    {
        "code": "CORE_9_18",
        "name": "Developpement precoce (9-18 mois)",
        "age_min_months": 9,
        "age_max_months": 18,
        "is_core": True,
        "question_codes": ["SOC_01", "SOC_02"],
    },
    {
        "code": "CORE_12_30",
        "name": "Communication et socialisation (12-30 mois)",
        "age_min_months": 12,
        "age_max_months": 30,
        "is_core": True,
        "question_codes": [
            "COM_01", "COM_03", "SOC_01", "SOC_02", "SOC_03",
            "SOC_04", "SOC_05", "BEH_01", "SEN_01", "SEN_02",
        ],
    },
    {
        "code": "CORE_18_48",
        "name": "Developpement global (18-48 mois)",
        "age_min_months": 18,
        "age_max_months": 48,
        "is_core": True,
        "question_codes": [
            "COM_01", "COM_02", "COM_03", "SOC_01", "SOC_02",
            "SOC_03", "SOC_04", "SOC_05", "BEH_01", "BEH_02",
            "SEN_01", "SEN_02",
        ],
    },
    {
        "code": "CORE_48_72",
        "name": "Developpement avance (48-72 mois)",
        "age_min_months": 48,
        "age_max_months": 72,
        "is_core": True,
        "question_codes": [
            "COM_03", "COM_04", "SOC_01", "SOC_02", "SOC_05",
            "SOC_06", "SOC_07", "BEH_01", "BEH_02", "BEH_03",
            "SEN_01", "SEN_02", "SEN_03",
        ],
    },
    {
        "code": "CORE_72_144",
        "name": "Enfant d'age scolaire (6-12 ans)",
        "age_min_months": 72,
        "age_max_months": 144,
        "is_core": True,
        "question_codes": [
            "COM_03", "COM_04", "COM_05",
            "SOC_01", "SOC_02", "SOC_05", "SOC_06", "SOC_07", "SOC_08",
            "BEH_01", "BEH_02", "BEH_03", "BEH_04",
            "SEN_01", "SEN_02", "SEN_03",
        ],
    },
]

PROVIDERS_DATA = [
    {
        "name": "Dr. Sophie Martin",
        "specialty": "Neuropediatre",
        "address": "25 boulevard Haussmann",
        "city": "Paris",
        "postal_code": "75009",
        "lat": 48.8738,
        "lng": 2.3370,
        "phone": "01 42 00 00 01",
    },
    {
        "name": "Dr. Pierre Durand",
        "specialty": "Pedopsychiatre",
        "address": "10 rue de Rivoli",
        "city": "Paris",
        "postal_code": "75004",
        "lat": 48.8566,
        "lng": 2.3522,
        "phone": "01 42 00 00 02",
    },
    {
        "name": "Cabinet Orthophonie Leroy",
        "specialty": "Orthophoniste",
        "address": "5 place de la Republique",
        "city": "Paris",
        "postal_code": "75011",
        "lat": 48.8676,
        "lng": 2.3639,
        "phone": "01 42 00 00 03",
    },
    {
        "name": "Dr. Marie Petit",
        "specialty": "Pediatre du developpement",
        "address": "15 avenue de la Gare",
        "city": "Lyon",
        "postal_code": "69003",
        "lat": 45.7604,
        "lng": 4.8600,
        "phone": "04 72 00 00 01",
    },
    {
        "name": "Centre de Diagnostic TSA Marseille",
        "specialty": "Neuropediatre",
        "address": "30 rue Paradis",
        "city": "Marseille",
        "postal_code": "13006",
        "lat": 43.2891,
        "lng": 5.3800,
        "phone": "04 91 00 00 01",
    },
]


class Command(BaseCommand):
    help = "Seed the database with screening questions, blocks, and sample providers"

    def handle(self, *args, **options):
        self._seed_questions()
        self._seed_blocks()
        self._seed_providers()
        self.stdout.write(self.style.SUCCESS("Seed data loaded successfully."))

    def _seed_questions(self):
        for q_data in QUESTIONS_DATA:
            options = q_data.pop("options")
            question, created = Question.objects.update_or_create(
                code=q_data["code"], defaults=q_data
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} question: {question.code}")

            for idx, opt in enumerate(options):
                opt["order_index"] = idx
                QuestionOption.objects.update_or_create(
                    question=question,
                    value=opt["value"],
                    defaults=opt,
                )

    def _seed_blocks(self):
        for b_data in BLOCKS_DATA:
            q_codes = b_data.pop("question_codes")
            block, created = QuestionBlock.objects.update_or_create(
                code=b_data["code"], defaults=b_data
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} block: {block.code}")

            BlockQuestion.objects.filter(block=block).delete()
            for idx, code in enumerate(q_codes):
                try:
                    question = Question.objects.get(code=code)
                    BlockQuestion.objects.create(
                        block=block, question=question, order_index=idx
                    )
                except Question.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"  Question {code} not found, skipping")
                    )

    def _seed_providers(self):
        from screening.models import Provider

        for p_data in PROVIDERS_DATA:
            provider, created = Provider.objects.update_or_create(
                name=p_data["name"], defaults=p_data
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} provider: {provider.name}")
