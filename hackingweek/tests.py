from django.test import TestCase

from hackingweek.models import Challenge

class ChallengeMethodTests(TestCase):

    def test_unknown_category(self):
        mychall = Challenge()
        self.assertRaises(ValueError, mychallcategory = 'a')
