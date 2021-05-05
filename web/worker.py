from jobs import q, apply_change


@q.worker
def execute_job(jid):
    print("Processing job {}".format(jid))
    apply_change(jid)

execute_job()

