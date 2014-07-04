from __future__ import print_function

import logging
logging.basicConfig(level=logging.DEBUG)
import uwsgi
import gevent
import flask
from flask_sqlalchemy import SQLAlchemy


def gevent_waiter(fd, hub=gevent.hub.get_hub()):
    hub.wait(hub.loop.io(fd, 1))

def gevent_id():
    return id(gevent.getcurrent())


#from sqlalchemy import exc
#from sqlalchemy import event
#from sqlalchemy.pool import Pool
#@event.listens_for(Pool, "checkout")
#def ping_connection(dbapi_connection, connection_record, connection_proxy):
#    print('checkout %d' % gevent_id())


# See https://github.com/mitsuhiko/flask-sqlalchemy/pull/67
class MySQLAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        # 1. Set waiter to connection.
        options['connect_args'] = {'waiter': gevent_waiter}
        super(MySQLAlchemy, self).apply_driver_hacks(app, info, options)


app = flask.Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/test'
# 2. Set scopefunc
db = MySQLAlchemy(app, session_options={'scopefunc': gevent_id})


@app.route('/')
def index():
    print("start: %d" % gevent_id())
    db.session.execute("SELECT SLEEP(1)")
    print("end: %d" % gevent_id())
    return b'xyz'
