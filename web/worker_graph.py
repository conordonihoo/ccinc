from jobs import q2, generate_graph
import sys


@q2.worker
def execute_job(jid):
    print("Processing graphing job {}".format(jid), file=sys.stderr)
    generate_graph(jid)

execute_job()

