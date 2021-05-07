from jobs import q1, transaction_change, generate_random_accounts
from datetime import date

@q1.worker
def execute_job(jid):
    if jid == "generate random accounts":
        print("Generating 100 random accounts")
        generate_random_accounts(50, 200, 2000, date(2000, 1, 1), date(2020, 1, 1), 15, 20)
        generate_random_accounts(50, 200, 2000, date(2000, 1, 1), date(2020, 1, 1), 75, 15)
    else:
        print("Processing transaction job {}".format(jid))
        transaction_change(jid)

execute_job()

