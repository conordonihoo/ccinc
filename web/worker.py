from jobs import q, apply_change

@q.worker
def execute_job(jid):
    apply_change(jid)

execute_job()
