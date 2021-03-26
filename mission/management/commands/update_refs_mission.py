from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from mission.models.mission_status import MissionStatus
from mission.models.mission_category import MissionCategory


class Command(BaseCommand):
    help = "Insert datas in mission ref tables - Defining MISSION_STATUS and MISSION_CATEGORY with corresponding datas in settings of the project is required"

    def handle(self, *args, **options):
        self.stdout.write("----------------- START UPDATES ON mission -----------------")

        if (settings.MISSION_STATUS is None):
            raise CommandError('MISSION_STATUS not found in settings')
        for mission_status in settings.MISSION_STATUS:
            if not MissionStatus.objects.filter(label__iexact=mission_status):
                new_mission_status = MissionStatus(label=mission_status)
                new_mission_status.save()
                self.stdout.write("Adding new mission status into database : {}".format(new_mission_status))
            else:
                self.stdout.write("Existing mission status : {}".format(mission_status))

        if (settings.MISSION_CATEGORY is None):
            raise CommandError('MISSION_CATEGORY not found in settings')
        for mission_category in settings.MISSION_CATEGORY:
            if not MissionCategory.objects.filter(label__iexact=mission_category['label']):
                new_mission_category = MissionCategory(
                    label=mission_category['label'], 
                    base_reward_amount=mission_category['default_reward'],
                    xp_amount=mission_category['xp_amount']
                )
                new_mission_category.save()
                self.stdout.write("Adding new mission category into database : {}".format(new_mission_category))
            else:
                self.stdout.write("Existing mission category : {}".format(mission_category))

        self.stdout.write("----------------- END UPDATES ON mission -----------------")
