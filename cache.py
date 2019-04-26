from pymemcache.client.hash import HashClient

class MetricCache:

    def __init__(self, server_list):
        # server_list = list of (host,port)
        self.client = HashClient(server_list)

    def increment(self, *, metric_name, value):
        if not self.client.get(metric_name):
            self.client.set(metric_name, 0)
        return self.client.incr(metric_name, value)


