import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            type=int,
            help='Data size coefficient',
        )

    def handle(self, *args, **options):
        ratio = options['ratio']

        if ratio <= 0:
            self.stdout.write(self.style.ERROR('Ratio must be positive'))
            return

        fake = Faker('ru_RU')

        users_count = ratio
        tags_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        likes_count = ratio * 200

        self.stdout.write('Start filling database...')

        with transaction.atomic():
            self.stdout.write('Deleting old data...')

            AnswerLike.objects.all().delete()
            QuestionLike.objects.all().delete()
            Answer.objects.all().delete()
            Question.objects.all().delete()
            Tag.objects.all().delete()
            Profile.objects.all().delete()

            User.objects.exclude(is_superuser=True).delete()

            self.stdout.write('Creating users...')

            users = [
                User(
                    username=f'user_{i}_{fake.user_name()}',
                    email=fake.email(),
                )
                for i in range(users_count)
            ]

            users = User.objects.bulk_create(users, batch_size=1000)

            profiles = [
                Profile(user=user)
                for user in users
            ]

            Profile.objects.bulk_create(profiles, batch_size=1000)

            self.stdout.write('Creating tags...')

            tags = [
                Tag(
                    name=f'tag_{i}',
                    slug=f'tag-{i}',
                )
                for i in range(tags_count)
            ]

            tags = Tag.objects.bulk_create(tags, batch_size=1000)

            self.stdout.write('Creating questions...')

            questions = [
                Question(
                    author=random.choice(users),
                    title=f'{fake.sentence(nb_words=8).rstrip(".!?")}?',
                    text=fake.text(max_nb_chars=700),
                    rating=random.randint(-10, 100),
                )
                for _ in range(questions_count)
            ]

            questions = Question.objects.bulk_create(questions, batch_size=1000)

            self.stdout.write('Adding tags to questions...')

            question_tags = []

            for question in questions:
                selected_tags = random.sample(tags, k=min(3, len(tags)))

                for tag in selected_tags:
                    question_tags.append(
                        Question.tags.through(
                            question_id=question.id,
                            tag_id=tag.id,
                        )
                    )

            Question.tags.through.objects.bulk_create(
                question_tags,
                batch_size=1000,
                ignore_conflicts=True,
            )

            self.stdout.write('Creating answers...')

            answers = [
                Answer(
                    question=random.choice(questions),
                    author=random.choice(users),
                    text=fake.text(max_nb_chars=500),
                    rating=random.randint(-5, 50),
                    is_correct=random.choice([False, False, False, True]),
                )
                for _ in range(answers_count)
            ]

            answers = Answer.objects.bulk_create(answers, batch_size=1000)

            self.stdout.write('Creating question likes...')

            question_likes = []
            used_question_likes = set()

            while len(question_likes) < likes_count // 2:
                user = random.choice(users)
                question = random.choice(questions)
                key = (user.id, question.id)

                if key in used_question_likes:
                    continue

                used_question_likes.add(key)

                question_likes.append(
                    QuestionLike(
                        user=user,
                        question=question,
                        value=random.choice(
                            [QuestionLike.LIKE, QuestionLike.DISLIKE]
                        ),
                    )
                )

            QuestionLike.objects.bulk_create(question_likes, batch_size=1000)

            self.stdout.write('Creating answer likes...')

            answer_likes = []
            used_answer_likes = set()

            while len(answer_likes) < likes_count // 2:
                user = random.choice(users)
                answer = random.choice(answers)
                key = (user.id, answer.id)

                if key in used_answer_likes:
                    continue

                used_answer_likes.add(key)

                answer_likes.append(
                    AnswerLike(
                        user=user,
                        answer=answer,
                        value=random.choice(
                            [AnswerLike.LIKE, AnswerLike.DISLIKE]
                        ),
                    )
                )

            AnswerLike.objects.bulk_create(answer_likes, batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Database filled successfully'))
        self.stdout.write(f'Users: {users_count}')
        self.stdout.write(f'Profiles: {users_count}')
        self.stdout.write(f'Tags: {tags_count}')
        self.stdout.write(f'Questions: {questions_count}')
        self.stdout.write(f'Answers: {answers_count}')
        self.stdout.write(f'Likes: {likes_count}')