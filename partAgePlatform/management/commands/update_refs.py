from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from user.management.commands.update_refs_user import Command as UserRefCommand
from messaging.management.commands.update_refs_messaging import Command as MessagingRefCommand
from mission.management.commands.update_refs_mission import Command as MissionRefCommand

class Command(BaseCommand):
    help = "Call specific update_refs commands depending on params"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('apps_to_update', nargs='+', type=str)

    def handle(self, *args, **options):
        separator = ', '
        commands_called = separator.join(options['apps_to_update'])

        self.stdout.write("****************************************************************")
        self.stdout.write("START DATABASE_UPDATE FOR - {} - AT {}".format(commands_called, datetime.now()))
        self.stdout.write("****************************************************************")

        if ('all' in commands_called):
            commands = (
                UserRefCommand(), 
                MessagingRefCommand(),
                MissionRefCommand(),
            )
            
            for command in commands:
                command.handle()
        else:
            for app_name in options['apps_to_update']:
                if (app_name == 'user'):
                    command = UserRefCommand()
                    command.handle()
                elif(app_name == 'messaging'):
                    command = MessagingRefCommand()
                    command.handle()
                elif(app_name == 'mission'):
                    command = MissionRefCommand()
                    command.handle()
                else:
                    raise CommandError("No command associated to '{}' app".format(app_name))

        self.stdout.write("****************************************************************")
        self.stdout.write("REFS UPDATES FOR {} - DONE".format(commands_called))
        self.stdout.write("****************************************************************")
