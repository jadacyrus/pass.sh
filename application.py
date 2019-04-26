from bottle import Bottle, request, response, template, static_file, hook, redirect
import os, sys
import settings
import uuid
import time
from password_encrypter import PasswordEncrypter
from dynamo_backend import DynamoBackend
from urllib.parse import urljoin
from validation import Validator
from metrics import MetricStore
from cache import MetricCache

class PassSh(Bottle):
    
    def __init__(self):
        super().__init__()
        self.establish_environment()
        self.route("/", method = "GET", callback = self.index)
        self.route("/show/<uuid>", method = "GET", callback = self.show)
        self.route("/create", method = "POST", callback = self.create)
        self.route("/static/<filename>", method = "GET", callback = self.static)
        self.route("/healthz", method = "GET", callback = self.healthcheck)
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
        self.ENV_MAX_DAYS = os.environ.get('ENV_MAX_DAYS', 5)
        self.ENV_MAX_VIEWS = os.environ.get('ENV_MAX_VIEWS', 10)
        self.ENV_INFLUXDB_HOST = os.environ.get('ENV_INFLUXDB_HOST', 'localhost')
        self.ENV_INFLUXDB_PORT = os.environ.get('ENV_INFLUXDB_PORT', 8086)
        self.ENV_INFLUXDB_DB = os.environ.get('ENV_INFLUXDB_DB', 'pass')
        self.ENV_MEMCACHED_HOST = os.environ.get('ENV_MEMCACHED_HOST', 'localhost')
        self.ENV_MEMCACHED_PORT = os.environ.get('ENV_MEMCACHED_PORT', 11211)

    def start(self):
        print('Password sharing service is alive')
        self.run(host = self.ENV_HOST, port = int(self.ENV_PORT), server = self.ENV_BACKEND, debug = int(self.ENV_DEBUG))
    
    def bump_metric(self, field, **kwargs):
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

    def index(self):
        return template('index', max_days = self.ENV_MAX_DAYS, max_views = self.ENV_MAX_VIEWS)

    def show(self, uuid):
        item = self.dynamo_backend.get(uuid)
        if 'Item' in item:
            secret = item['Item']['secret']
            views_remaining = item['Item']['views_remaining']
            _id = item['Item']['uuid']
            if views_remaining > 0:
                views_remaining = views_remaining - 1
                plaintext_secret = self.password_encrypter.decrypt(secret)
                self.dynamo_backend.increment(_id, 'views_remaining', -1)
                self.bump_metric('show_success')
                return template('show', plaintext = plaintext_secret, views = views_remaining)
            else:
                self.bump_metric('show_spent')
                return template('index', error = 'The link you are trying to access is no longer valid')
        else:
            self.bump_metric('show_expired')
            return template('index', error = 'The link you are trying to access is no longer valid')

    def create(self):
        request_type, params = self.parse_request()
        if self.validate_params(params):
            if params['secret']:
                success, url = self.create_secret(params['secret'],
                        params['views'],
                        params['days'])
                if success: 
                    self.bump_metric('create_success')
                    if request_type == 'web':
                        return template('share', url = url, days = params['days'], views = params['views'])
                    else:
                        return { 'url': url, 'days': params['days'], 'views': params['views'] } 

                else:
                    self.bump_metric('create_fail_db')
                    return template('index', error = 'Backend service is unavailable')
            else:
                self.bump_metric('create_fail_empty')
                return template('index', error = 'Nothing in payload')
        else:
            self.bump_metric('create_fail_invalid')
            return template('index', error = 'Invalid parameters specified')

    def healthcheck(self):
        return 'This is the password sharing service. Go away!'

    def static(self, filename):
        return static_file(filename, root = 'static/')

    def create_secret(self, secret, views, days):
        encrypted_secret = self.password_encrypter.encrypt(secret)
        expires_at = int(time.time() + int(days) * 864000)
        _id = str(uuid.uuid4())
        item = { 'uuid': _id, 'ttl': expires_at, 'views_remaining': int(views), 'secret': encrypted_secret }
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

        return self.validator.is_valid_password(secret) and self.validator.is_valid_days(days) and self.validator.is_valid_views(views)

if __name__ == '__main__':
    service = PassSh()
    service.start()
