from django.test import TestCase

from hackingweek.models import Category, Challenge

def wrong_challenge():
    chall = Challenge()
    chall.category = 'a'

class ChallengeMethodTests(TestCase):

    def test_unknown_category(self):
        self.assertRaises(ValueError, wrong_challenge)

    def test_Challenge_creation(self):
        chall = Challenge()
        mycat = Category('my category')
        chall.category = mycat
        chall.name = 'my challenge'
        chall.author = 'anonymous'
        chall.body = 'No comment'
        chall.key = '12345'
