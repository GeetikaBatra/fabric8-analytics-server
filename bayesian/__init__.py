import logging

from flask import Flask
from flask import Response
from flask import g
from flask import redirect
from flask import request
from flask import url_for
from flask_appconfig import AppConfig
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, send, disconnect
from flask_cors import CORS
from cucoslib.schemas import SchemaRef
from cucoslib.utils import (safe_get_latest_version, get_dependents_count, get_component_percentile_rank,
                            usage_rank2str, MavenCoordinates)
# from .utils import get_analyses_from_graph
# from requests import get, post, exceptions
def setup_logging(app):
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        app.logger.addHandler(handler)

# we must initialize DB here to not create import loop with .auth...
#  flask really sucks at this
rdb = SQLAlchemy()


def create_app(configfile=None):
    # do the imports here to not shadow e.g. "import bayesian.frontend.api_v1"
    # by Blueprint imported here
    from .api_v1 import api_v1
    from .exceptions import HTTPError
    from .utils import JSONEncoderWithExtraTypes
    app = Flask(__name__)
    
    AppConfig(app, configfile)

    # actually init the DB with config values now
    rdb.init_app(app)
    app.rdb = rdb

    # We need JSON encoder that can serialize datetime.datetime
    app.json_encoder = JSONEncoderWithExtraTypes

    app.register_blueprint(api_v1)
    # Redirect to latest API version if /api is accessed
    app.route('/api')(lambda: redirect(url_for('api_v1.apiendpoints__slashless')))
    # Likewise for base URL, and make that accessible by name
    @app.route('/')
    def base_url():
        return redirect(url_for('api_v1.apiendpoints__slashless'))

    @app.errorhandler(HTTPError)
    def handleerrors(e):
        bp = app.blueprints.get(request.blueprint)
        # if there's an error pre-request (e.g. during authentication) in non-GET requests,
        #  request.blueprint is not set yet
        if not bp:
            # sort by the length of url_prefix, filter out blueprints without prefix
            bps = reversed(sorted(
                [(name, b) for name, b in app.blueprints.items() if b.url_prefix is not None],
                key=lambda tpl: len(tpl[1].url_prefix)))
            for bp_name, b in bps:
                if request.environ['PATH_INFO'].startswith(b.url_prefix):
                    bp = b
                    break
        if bp:
            handler = getattr(bp, 'coreapi_http_error_handler', None)
            if handler:
                return handler(e)
        return Response(e.error, status=e.status_code)

    setup_logging(app)

    @app.before_request
    def set_current_user():
        g.current_user = None

    return app


app = create_app()
CORS(app)

socketio = SocketIO(app)
# def generate_recommendation(data, package, version):
#     # Template Dict for recommendation
#     reco = {
#         'recommendation': {
#             'component-analyses': {},
#         }
#     }
#     if data:
#         # Get the Latest Version
#         latest_version = data[0].get('package', {}).get('latest_version', [None])[0]
#         message = ''
#         max_cvss = 0.0
#         # check if given version has a CVE or not
#         for records in data:
#             ver = records['version']
#             if version == ver.get('version', [''])[0]:
#                 records_arr = []
#                 records_arr.append(records)
#                 reco['data'] = records_arr
#                 cve_ids = []
#                 cve_maps = []
#                 if ver.get('cve_ids', [''])[0] != '':
#                     message = 'CVE/s found for Package - ' + package + ', Version - ' + version + '\n'
#                     # for each CVE get cve_id and cvss scores
#                     for cve in ver.get('cve_ids'):
#                         cve_id = cve.split(':')[0]
#                         cve_ids.append(cve_id)
#                         cvss = float(cve.split(':')[1])
#                         cve_map = {
#                             'id': cve_id,
#                             'cvss': cvss
#                         }
#                         cve_maps.append(cve_map)
#                         if cvss > max_cvss:
#                             max_cvss = cvss
#                     message += ', '.join(cve_ids)
#                     message += ' with a max cvss score of - ' + str(max_cvss)
#                     reco['recommendation']['component-analyses']['cve'] = cve_maps
#                     break
#                 else:
#                     reco['recommendation'] = {}
#                     return {"result": reco}

#         # check if latest version exists or current version is latest version
#         if not latest_version or latest_version == '' or version == latest_version:
#             if message != '':
#                 reco['recommendation']['message'] = message
#             return {"result": reco}
#         # check if latest version has lower CVEs or no CVEs than current version
#         for records in data:
#             ver = records['version']
#             if latest_version == ver.get('version', [''])[0]:
#                 if ver.get('cve_ids', [''])[0] != '':
#                     for cve in ver.get('cve_ids'):
#                         cvss = float(cve.split(':')[1])
#                         if cvss >= max_cvss:
#                             break
#                 message += '\n It is recommended to use Version - ' + latest_version
#                 reco['recommendation']['change_to'] = latest_version
#                 reco['recommendation']['message'] = message
#     return {"result": reco}

# def get_analyses_from_graph (ecosystem, package, version):
#     print("reache byesian")
#     print("new")
#     print(os.environ.get("BAYESIAN_GREMLIN_HTTP_SERVICE_HOST", "localhost"))
#     url = "http://{host}:{port}".format\
#             (host=os.environ.get("BAYESIAN_GREMLIN_HTTP_SERVICE_HOST", "localhost"),\
#              port=os.environ.get("BAYESIAN_GREMLIN_HTTP_SERVICE_PORT", "8182"))
#     print("bayesian url")
#     print(url)
#     qstring = "g.V().has('ecosystem','" + ecosystem + "').has('name','" + package + "')" \
#               ".as('package').out('has_version').as('version').select('package','version').by(valueMap());"
#     payload = {'gremlin': qstring}
#     print("payload")
#     print(payload)
#     try:
#         graph_req = post(url, data=json.dumps(payload))
#         print("graph+req", graph_req.json())
#     except:
#         return "error"

#     resp = graph_req.json()

#     if 'result' not in resp:
#         return None
#     if len(resp['result']['data']) == 0:
#         # trigger unknown component flow in API for missing package
#         return None

#     data = resp['result']['data']
#     resp = generate_recommendation(data, package, version)

#     if 'data' not in resp.get('result'):
#         # trigger unknown component flow in API for missing version
#         return None

#     return resp
# @socketio.on('echo')
# def handle_my_custom_namespace_event(jsn):
#     print('received json: ' + str(jsn))
#     return {'msg': jsn}

# @socketio.on('echo', namespace='/test')
# def ping_pong(msg):
#     print("reached here")
#     print(msg)
#     # import pdb
#     # pdb.set_trace()
#     schema_ref = SchemaRef('analyses_graphdb', '1-2-0')
#     ecosystem = "npm"
#     package = "serve-static"
#     version = "1.7.1"
#     # if ecosystem == 'maven':
#     #     package = MavenCoordinates.normalize_str(package)
#     print("befire ")
#     # emit("my_response", "test success")
#     # disconnect()
#     result = get_analyses_from_graph(ecosystem, package, version)
#     # current_app.logger.warn( "%r" % result)
#     print("here")
#     print("result", result)
#     disconnect()
#     if result != None:
#         print("result is not none")
#         # Known component for Bayesian
#         print(result)
#         emit("my_response", result)
#         disconnect()

# @socketio.on('connect', namespace='/test')
# def test_connect():
#     global thread
#     if thread is None:
#         thread = socketio.start_background_task(target=background_thread)
#     emit('my_response', {'data': 'Connected', 'count': 0})

# from . import filters
from . import websocket_test