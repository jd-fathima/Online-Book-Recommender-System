"""Unit tests for the Ratings model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Rating, Book


class RatingsModelsTestCase(TestCase):
    fixtures = ["bookclub/tests/fixtures/default_ratings.json",
                "bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_books.json",
                ]

    def setUp(self):
        self.rating_one = Rating.objects.get(pk=1)
        self.rating_two = Rating.objects.get(pk=2)
        self.john = User.objects.get(pk=1)
        self.book_one = Book.objects.get(pk=1)

    # Rating tests
    def test_ratings_cannot_be_below_0(self):
        self.rating_one.rating = -1
        self._assert_rating_is_invalid()

    def test_ratings_cannot_be_above_10(self):
        self.rating_one.rating = 11
        self._assert_rating_is_invalid()

    def test_ratings_may_be_5(self):
        self.rating_one.rating = 5
        self._assert_rating_is_valid()

    def test_ratings_cannot_be_string(self):
        self.rating_one.rating = "abc"
        self._assert_rating_is_invalid()

    def test_ratings_cannot_be_empty(self):
        self.rating_one.rating = None
        self._assert_rating_is_invalid()

    def test_rating_must_have_all_fields_simultaneously(self):
        self.assertEqual(self.john, self.rating_one.user)
        self.assertEqual(self.book_one, self.rating_one.book)
        self.assertEqual(5, self.rating_one.rating)

    def test_rating_user_exists(self):
        self.assertEqual(self.rating_one.user, self.john)

    def test_rating_rating_must_exist(self):
        self.rating_one.rating = None
        self._assert_rating_is_invalid()

    def test_rating_user_getter_works(self):
        self.assertEqual(self.rating_one.get_user(),self.rating_one.user)

    def test_rating_book_getter_works(self):
        self.assertEqual(self.rating_one.get_book(),self.rating_one.book)
        
    def test_rating_rating_getter_works(self):
        self.assertEqual(self.rating_one.get_rating(),self.rating_one.rating)

    def _assert_rating_is_valid(self):
        try:
            self.rating_one.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')
            
    def test_validity_test_fails_when_rating_is_invalid(self):
        self.rating_one.rating = 747
        with self.assertRaisesMessage(AssertionError, 'Test club should be valid'):
            self._assert_rating_is_valid()

    def _assert_rating_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rating_one.full_clean()