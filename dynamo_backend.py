import boto3

class DynamoBackend:

  def __init__(self, table_name, region):
      d = boto3.resource('dynamodb', region_name = region)
      self.table = d.Table(table_name)

  def put(self, item):
      response = self.table.put_item(Item = item)
      return response

  def get(self, key):
      response = self.table.get_item(Key = { 'uuid': key })
      return response

  def increment(self, key, attribute, value):
      response = self.table.update_item(Key = { 'uuid': key },
              UpdateExpression = "set views_remaining = views_remaining + :val",
              ExpressionAttributeValues = { ":val": value })
      return response

