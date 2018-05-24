class Validator:
    def __init__(self, max_pw_length, max_days, max_views):
        self.min_pw_length = 1
        self.min_days = 1
        self.min_views = 1

        self.max_pw_length = max_pw_length
        self.max_days = max_days
        self.max_views = max_views

    def is_valid_password(self, password):
        pw_len = len(password)
        return pw_len >= self.min_pw_length and pw_len <= self.max_pw_length

    def is_valid_days(self, days):
        days_len = int(days)
        return days_len >= self.min_days and days_len <= self.max_days and days.isnumeric()

    def is_valid_views(self, views):
        views_len = int(views)
        return views_len >= self.min_views and views_len <= self.max_views and views.isnumeric()
