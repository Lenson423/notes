from django.test import TestCase
from django.contrib.auth.models import User
from .models import Note, generate_unique_slug
from django.utils.text import slugify
from django.core.signing import BadSignature


class NoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.note = Note.objects.create(
            user=self.user,
            note_title="Test Note",
            note_content="This is a test note content"
        )

    def test_generate_unique_slug(self):
        slug = generate_unique_slug(Note, "Test Note")
        self.assertEqual(slug, "test-note")

        Note.objects.create(user=self.user, note_title="Test Note")
        slug2 = generate_unique_slug(Note, "Test Note")
        self.assertEqual(slug2, "test-note-1")

    def test_note_creation(self):
        self.assertEqual(self.note.note_title, "Test Note")
        self.assertEqual(self.note.slug, slugify("Test Note"))
        self.assertEqual(self.note.note_content, "This is a test note content")

    def test_get_message_as_markdown(self):
        expected_html = '<p>This is a test note content</p>'
        self.assertIn(expected_html, self.note.get_message_as_markdown())

    def test_get_signed_hash(self):
        signed_hash = self.note.get_signed_hash()
        self.assertTrue(signed_hash.startswith(f"{self.note.pk}:"))

    def test_get_absolute_url(self):
        expected_url = f"/share_notes/{self.note.get_signed_hash()}/"
        self.assertEqual(self.note.get_absolute_url(), expected_url)

    def test_slug_update_on_title_change(self):
        self.note.note_title = "Updated Note Title"
        self.note.save()
        self.assertEqual(self.note.slug, slugify("Updated Note Title"))

    def test_signed_hash_validation(self):
        signed_hash = self.note.get_signed_hash()
        self.assertEqual(Note.signer.unsign(signed_hash), str(self.note.pk))

        with self.assertRaises(BadSignature):
            Note.signer.unsign("invalid:hash")


class AddNoteFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_valid_form(self):
        form_data = {
            'note_title': "Valid Note",
            'note_content': "This is valid content",
            'tags': "tag1, tag2",
        }
        form = AddNoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_fields(self):
        form_data = {
            'note_content': "Missing title",
        }
        form = AddNoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('note_title', form.errors)
