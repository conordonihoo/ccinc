from jobs import q1, transaction_change


@q1.worker
def execute_job(jid):
    print("Processing transaction job {}".format(jid))
    transaction_change(jid)

execute_job()

