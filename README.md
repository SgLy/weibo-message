## Weibo Message Crawler

### Aim
Crawl all messages of a user with username and password, and generate a excel table.

### Login code
[xchaoinfo/fuck-login](https://github.com/xchaoinfo/fuck-login)

### Usage
create `login.py` under root directory with content like:
```
username = 'you@yourmail.com`
password = 'yourpasswd'
```

create a virtualenv:
```bash
virtualenv -p /usr/bin/python3 env
env/bin/pip install -r requirements.txt
```

run `main.py`:
```bash
./main.py
```
