# Health Fair App

Vital Signs Hackathon Project

## Setup

Create virtualenv:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create database (first create user, add to env vars in `health_fair/settings/base.py`),
then run:
`python manage.py migrate`
