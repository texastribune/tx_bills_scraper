BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_PASSWORD = "va5byzilgul0nuip"
BROKER_VHOST = "org.texastribune.bills"
BROKER_USER = "bills"

CELERY_RESULT_BACKEND = "amqp"

CELERY_IMPORTS = ("tasks", )

# CELERY_ALWAYS_EAGER = True
