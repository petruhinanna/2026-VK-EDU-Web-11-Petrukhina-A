from django.db import migrations


INDEX_NAME = 'questions_question_full_text_idx'


def create_full_text_index(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    schema_editor.execute(f'''
        CREATE INDEX IF NOT EXISTS {INDEX_NAME}
        ON questions_question
        USING GIN (
            to_tsvector(
                'simple',
                coalesce(title, '') || ' ' || coalesce(text, '')
            )
        );
    ''')


def drop_full_text_index(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    schema_editor.execute(f'DROP INDEX IF EXISTS {INDEX_NAME};')


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_answer_is_active_answer_updated_at_and_more'),
    ]

    operations = [
        migrations.RunPython(
            create_full_text_index,
            drop_full_text_index,
        ),
    ]