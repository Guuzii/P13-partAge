from datetime import datetime

from user.models.user_type import UserType
from user.models.custom_user import CustomUser
from user.models.wallet import Wallet

def cronjob_senior_income():
    senior_type = UserType.objects.get(label='senior')
    senior_users = CustomUser.objects.filter(user_type=senior_type)
    senior_wallets_pk = []

    for senior in senior_users:
        senior_wallets_pk.append(senior.wallet.pk)

    senior_wallets = Wallet.objects.filter(pk__in=senior_wallets_pk)

    for wallet in senior_wallets:
        wallet.balance += 1000
        wallet.save()

    print("Cron senior_regular_income OK - {}".format(datetime.now()))
