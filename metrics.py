from influxdb import InfluxDBClient
import socket

class MetricStore:

    def __init__(self, influx_options):
        host, port, db = influx_options
        self.client = InfluxDBClient(host=host, port=int(port))
        self.client.switch_database(db)
        self.tag_host = socket.getfqdn()

    def metric(self, *, measurement, field, value, tags):
        json_body = [{
            "measurement": measurement,
            "tags": {
                "host": self.tag_host
                },
            "fields": {
                field: value
                }}]
        for k, v in tags.items():
            json_body[0]['tags'][k] = v
        self.client.write_points(json_body)



