# pass.sh

- Uses python [cryptography library](https://cryptography.io/en/latest/fernet/) (symmetric encryption) to encrypt all passwords
- Storage backend is [AWS Dynamo DB](https://aws.amazon.com/dynamodb/)
- Web framework is [Bottle](https://www.bottlepy.org)

### API

request:

```bash
curl -X POST https://pass.sh/create -H 'Content-Type:application/json' \
  --data '{"secret":"foobar", "days": "5", "views": "10"}'
```

with IP whitelist

```bash
curl -X POST https://pass.sh/create -H 'Content-Type:application/json' \
  --data '{"secret":"foobar", "days": "5", "views": "10", "ip": "2601:87:80:1811:90f7:67b9:4747:64a4"}'
```

response:

```json
{"days": "5", "url": "https://pass.sh/show/3625c429-c93e-41d2-a5c9-0a886e162b76", "views": "10"}
```
