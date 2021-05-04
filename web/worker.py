from jobs import q, apply_change

@q.worker
def execute_job(bid):
    apply_change(bid)

execute_job()
