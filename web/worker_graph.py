from jobs import q2, graph_change


@q2.worker
def execute_job(jid):
    print("Processing graphing job {}".format(jid))
    graph_change(jid)

execute_job()

