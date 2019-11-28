import ipaddress

class Validator:
    def __init__(self, max_pw_length, max_days, max_views):
        self.min_pw_length = 1
        self.min_days = 1
        self.min_views = 1

        self.max_pw_length = max_pw_length
        self.max_days = max_days
        self.max_views = max_views

    def is_valid_ip(self, ip):
        valid = self.__valid_ip
        if valid(ipaddress.ip_network, ip):
            return True, ''
        return False, 'Invalid IP: {}. Please enter a valid IP range'.format(ip)

    def __valid_ip(self, proto, ip):
        try:
            proto(ip)
            return True
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
            return False

    def is_valid_password(self, password):
        try:
            pw_len = len(password)
            return pw_len >= self.min_pw_length and pw_len <= self.max_pw_length, 'Please enter a valid secret'
        except:
            return False, 'Please enter a valid secret'

    def is_valid_days(self, days):
        try:
            days_len = int(days)
            return days_len >= self.min_days and days_len <= self.max_days and days.isnumeric(), 'Please enter a valid expiration range'
        except:
            return False, 'Please enter a valid expiration range'

    def is_valid_views(self, views):
        try:
            views_len = int(views)
            return views_len >= self.min_views and views_len <= self.max_views and views.isnumeric(), 'Please enter a valid number of views'
        except:
            return False, 'Please enter a valid number of views'
