from django.db import models, IntegrityError


class TeamJoinRequestManager(models.Manager):

    def delete_expired_requests(self):
        for request in self.all():
            if request.key_expired():
                request.delete()
