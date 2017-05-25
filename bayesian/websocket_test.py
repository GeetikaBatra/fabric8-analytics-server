from flask import Flask
from flask_socketio import SocketIO, emit, send, disconnect
from cucoslib.schemas import SchemaRef
from .utils import get_analyses_from_graph
from . import socketio
import json

# @socketio.on('echo')
# def handle_my_custom_namespace_event(jsn):
#     print('received json: ' + str(jsn))
#     return {'msg': jsn}

@socketio.on('get_component_analyses', namespace='/ws-component-analyses')
def wsComponentAnalyses(msg):
    print("msg")
    print(msg)
    print(type(msg))
    ecosystem = msg.get("ecosystem")
    package= msg.get("name")
    version = msg.get("version")
    # schema_ref = SchemaRef('analyses_graphdb', '1-2-0')
    # ecosystem = "npm"
    # anme = "serve-static"
    # version = "1.7.0"
    # if ecosystem == 'maven':
    #     package = MavenCoordinates.normalize_str(package)
    result = get_analyses_from_graph(ecosystem, package, version)
    print("reachesd here")
    print(result)
    if result != None:
        print("result is not none")
        # Known component for Bayesian
        print(result)
        emit("component_analyses_response", json.dumps(result))
        disconnect()
    disconnect()
# # # app = Flask(__name__)
# # # socketio = SocketIO(app)
# # # thread = None
# # # 
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
#     result = get_analyses_from_graph(ecosystem, package, version)
#     # current_app.logger.warn( "%r" % result)
#     print("here")
#     print("result", result)
#     if result != None:
#         print("result is not none")
#         # Known component for Bayesian
#         print(result)
#         emit("my_response", result)
#         # disconnect()

# # # @socketio.on('echo')
# # # def handle_my_custom_namespace_event(jsn):
# # #     print('received json: ' + str(jsn))
# # #     return {'msg': jsn}

# # # @socketio.on('echo', namespace='/test')
# # # def ping_pong(msg):

# # #     print(msg)
# # #     # import pdb
# # #     # pdb.set_trace()
# # #     schema_ref = SchemaRef('analyses_graphdb', '1-2-0')
# # #     ecosystem = "npm"
# # #     package = "serve-static"
# # #     version = "1.7.1"
# # #     if ecosystem == 'maven':
# # #         package = MavenCoordinates.normalize_str(package)
# # #     result = get_analyses_from_graph(ecosystem, package, version)
# # #     current_app.logger.warn( "%r" % result)

# # #     if result != None:
# # #         # Known component for Bayesian
# # #         print(msg)
# # #         emit("my_response", result)

# # # # @socketio.on('connect', namespace='/test')
# # # # def test_connect():
# # # #     global thread
# # # #     if thread is None:
# # # #         thread = socketio.start_background_task(target=background_thread)
# # # #     emit('my_response', {'data': 'Connected', 'count': 0})


# # # # def background_thread():
# # # #     """Example of how to send server generated events to clients."""
# # # #     count = 0
# # # #     while True:
# # # #         socketio.sleep(10)
# # # #         count += 1
# # # #         socketio.emit('my_response',
# # # #                       {'data': 'Server generated event', 'count': count},
# # # #                       namespace='/test')

# # # if __name__ == "__main__":
# # #     socketio.run(app, port=5012)