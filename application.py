from bottle import Bottle, request, response, template, static_file, hook, redirect
import os, sys
import settings
import uuid
import time
import ipaddress
from password_encrypter import PasswordEncrypter
from dynamo_backend import DynamoBackend
from urllib.parse import urljoin
from validation import Validator
from metrics import MetricStore
from cache import MetricCache

__VERSION__ = "0.0.3"

class PassSh(Bottle):

    def __init__(self):
        super().__init__()
        self.establish_environment()
        self.route("/", method = "GET", callback = self.index)
        self.route("/show/<uuid>", method = "GET", callback = self.show)
        self.route("/create", method = "POST", callback = self.create)
        self.route("/static/<filename>", method = "GET", callback = self.static)
        self.route("/healthz", method = "GET", callback = self.healthcheck)
        self.route("/sitemap.xml", method = "GET", callback = self.sitemap)
        self.add_hook("before_request", self.before_request)
        self.add_hook("after_request", self.after_request)

        self.password_encrypter = PasswordEncrypter(self.ENV_ENCRYPTION_KEY)
        self.dynamo_backend = DynamoBackend(self.ENV_TABLE_NAME, self.ENV_AWS_REGION)
        self.validator = Validator(self.ENV_MAX_PW_LENGTH, self.ENV_MAX_DAYS, self.ENV_MAX_VIEWS)
        self.metric_cache = MetricCache([(self.ENV_MEMCACHED_HOST, int(self.ENV_MEMCACHED_PORT))])
        self.metric_store = MetricStore((self.ENV_INFLUXDB_HOST, int(self.ENV_INFLUXDB_PORT), self.ENV_INFLUXDB_DB))

    def establish_environment(self):
        self.ENV_ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', None)
        if self.ENV_ENCRYPTION_KEY == None:
            print("No encryption key specified (ENCRYPTION_KEY not set). A key is required to start the service")
            sys.exit(1)
        self.ENV_HOST = os.environ.get('BIND_TO', '0.0.0.0')
        self.ENV_PORT = os.environ.get('PORT', 3000)
        self.ENV_BACKEND = os.environ.get('BACKEND', 'paste')
        self.ENV_TABLE_NAME = os.environ.get('TABLE_NAME', 'test_password_share')
        self.ENV_BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')
        self.ENV_AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
        self.ENV_DEBUG = os.environ.get('ENV_DEBUG', False)
        self.ENV_HANDLE_SSL_REDIRECT = os.environ.get('ENV_HANDLE_SSL_REDIRECT', True)
        self.ENV_MAX_PW_LENGTH = os.environ.get('ENV_MAX_PW_LENGTH', 4096)
        self.ENV_MAX_DAYS = os.environ.get('ENV_MAX_DAYS', 90)
        self.ENV_MAX_VIEWS = os.environ.get('ENV_MAX_VIEWS', 25)
        self.ENV_INFLUXDB_HOST = os.environ.get('ENV_INFLUXDB_HOST', 'localhost')
        self.ENV_INFLUXDB_PORT = os.environ.get('ENV_INFLUXDB_PORT', 8086)
        self.ENV_INFLUXDB_DB = os.environ.get('ENV_INFLUXDB_DB', 'pass')
        self.ENV_MEMCACHED_HOST = os.environ.get('ENV_MEMCACHED_HOST', 'localhost')
        self.ENV_MEMCACHED_PORT = os.environ.get('ENV_MEMCACHED_PORT', 11211)

    def start(self):
        print('Password sharing service is alive')
        self.run(host = self.ENV_HOST, port = int(self.ENV_PORT), server = self.ENV_BACKEND, debug = int(self.ENV_DEBUG))

    def bump_metric(self, field, **kwargs):
        return
        try:
            value = self.metric_cache.increment(metric_name=field, value=1)
            self.metric_store.metric(measurement='events',
                    field=field,
                    value=value,
                    tags=kwargs)
        except Exception as e:
            print("!!! bump_metric() failed with {}".format(e))

    def after_request(self):
        response.headers['strict-transport-security'] = "max-age=31536000; includeSubDomains"

    def before_request(self):
        if self.ENV_HANDLE_SSL_REDIRECT:
            scheme = request.get_header('X-Forwarded-Proto', None)
            if scheme and scheme != 'https':
                return redirect(urljoin(self.ENV_BASE_URL, request.path))
        return

    def index(self):
        return template('index', max_days = self.ENV_MAX_DAYS, max_views = self.ENV_MAX_VIEWS)

    def show(self, uuid):
        response.headers['referrer-policy'] = 'no-referrer'
        item = self.dynamo_backend.get(uuid)
        if 'Item' in item:
            _item = item['Item']
            secret = _item['secret']
            views_remaining = _item['views_remaining']
            _id = _item['uuid']
            ip = _item.get('ip', None)
            if ip:
                client_ip = ipaddress.ip_network(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
                allowed = False
                for ip in ip.split(','):
                    net = ipaddress.ip_network(ip)
                    if net.overlaps(client_ip):
                        allowed = True
                if not allowed:
                    return template('index', error = ['Not available from {}'.format(client_ip)])
            if views_remaining > 0:
                views_remaining = views_remaining - 1
                plaintext_secret = self.password_encrypter.decrypt(secret)
                self.dynamo_backend.increment(_id, 'views_remaining', -1)
                self.bump_metric('show_success')
                return template('show', plaintext = plaintext_secret, views = views_remaining)
            else:
                self.bump_metric('show_spent')
                return template('index', error = ['The link you are trying to access is no longer valid'])
        else:
            self.bump_metric('show_expired')
            return template('index', error = ['The link you are trying to access is no longer valid'])

    def create(self):
        request_type, params = self.parse_request()
        valid, errs = self.validate_params(params)
        if valid:
            success, url = self.create_secret(secret = params['secret'],
                    views = int(params['views']),
                    days = params['days'],
                    ip = params['ip'])

            if success:
                self.bump_metric('create_success')
                share_args = { 'url': url, 'days': params['days'], 'views': params['views'] }
                if request_type == 'web':
                    if params['ip'] and params['ip'].strip():
                        ip_list = params['ip'].split(',')
                        share_args['ip_list'] = ip_list

                    return template('share', **share_args)
                else:
                    return share_args
            else:
                self.bump_metric('create_fail_db')
                return template('index', error = ['Backend service is unavailable'])
        else:
            self.bump_metric('create_fail_invalid')
            return template('index', error = errs)

    def healthcheck(self):
        return 'This is the password sharing service. Go away!'

    def static(self, filename):
        return static_file(filename, root = 'static/')

    def sitemap(self):
        return static_file("sitemap.xml", root = 'static/')

    def create_secret(self, **kwargs):
        encrypted_secret = self.password_encrypter.encrypt(kwargs['secret'])
        expires_at = int(time.time() + int(kwargs['days']) * 864000)
        _id = str(uuid.uuid4())

        item = { 'uuid': _id, 'ttl': expires_at, 'views_remaining': int(kwargs['views']), 'secret': encrypted_secret }

        if kwargs['ip'] and kwargs['ip'].strip():
            item['ip'] = kwargs['ip']

        r = self.dynamo_backend.put(item)
        if r['ResponseMetadata']['HTTPStatusCode'] == 200:
            url = urljoin(self.ENV_BASE_URL, '/show/' + _id)
            return True, url
        else:
            return False, None

    def parse_request(self):
        if request.json:
            return 'json', request.json
        else:
            return 'web', request.params

    def validate_params(self, params):
        secret = params.get('secret', None)
        days = params.get('days', None)
        views = params.get('views', None)
        ip = params.get('ip', None)

        results = []
        results.append(self.validator.is_valid_password(secret))
        results.append(self.validator.is_valid_days(days))
        results.append(self.validator.is_valid_views(views))
        if ip:
            ips = ip.split(",")
            valid_ip = all(self.validator.is_valid_ip(ipaddr)[0] for ipaddr in ips)
            err_ip = ','.join(self.validator.is_valid_ip(ipaddr)[1] for ipaddr in ips)
            results.append((valid_ip, err_ip))

        return (all(result[0] for result in results), [result[1] if not result[0] else None for result in results])

if __name__ == '__main__':
    service = PassSh()
    service.start()
