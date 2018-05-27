from lib.wsgi import  WebSocketWSGI
from gevent.lock import Semaphore
from gevent.threadpool import ThreadPool as ThreadPool
from datetime import datetime
from random import randint
import time
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(levelname)-7s] -%(process)d:%(threadName)s:%(name)s:%(funcName)s - %(message)s')

pool = ThreadPool(1)
# demo app
import os
import random
def handle(ws):
    """  This is the websocket handler function.  Note that we
    can dispatch based on path in here, too."""
    if ws.path == '/echo':
        sem = Semaphore()
        while True:
            logger.debug("loop")
            data = ws.wait()
            logger.info("data {}".format(data))
            pool.apply_async(process, args=(data, ws,sem), callback=log_result)

    elif ws.path == '/data':
        for i in xrange(10000):
            ws.send("0 %s %s\n" % (i, random.random()))
            gevent.sleep(0.1)
    while True:
        logger.info ("loop")
        data = ws.recvmsg()
        pool.apply_async(process, args=(data, ws,sem), callback=log_result)

wsapp = WebSocketWSGI(handle)
def app(environ, start_response):
    """ This resolves to the web page or the websocket depending on
    the path."""
    for key,values in environ.items():
        logger.debug('{} : {}'.format(key,values))
    logger.info('new client connected from port {}'.format(environ['REMOTE_PORT']))
    if environ['PATH_INFO'] == '/' or environ['PATH_INFO'] == "":
        data = open(os.path.join(
                     os.path.dirname(__file__),
                     'websocket.html')).read()
        data = data % environ
        start_response('200 OK', [('Content-Type', 'text/html'),
                                 ('Content-Length', str(len(data)))])
        return [data]
    else:
        return wsapp(environ, start_response)

def process(data,ws,sem):
    logger.info('{} got data "{}"'.format(datetime.now().strftime('%H:%M:%S'), data))
    x = 1
    threshold = randint(1, 10)
    logger.info('threshold value {}'.format(threshold))
    start = int(time.time())
    current = 0
    while True:
        delta = int(time.time()) - start
        if (delta > threshold):
            break
        if (delta > current):
            current = current + 1
            logging.info('data {}'.format(data))
        x = x * x
    with sem:
        ws.send('data threshold {} '.format(res))
    return res

def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.

    logger.info("result :: ".format(result))
