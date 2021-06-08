import grpc
from protos import object_server_pb2_grpc as service_grpc
from protos import object_server_pb2 as service
import tello

# make an RPC request
channel = grpc.insecure_channel('localhost:50051')
stub = service_grpc.ObjectServiceStub(channel)

# request = service.ObjectRequest(ws="rtsp://root:1111@117.6.121.13:554/axis-media/media.amp")
# response = stub.LeaveObjectDetect(service.ObjectRequest(ws="rtsp://admin:abcd1234@172.16.10.84:554/Channels/101"))
# response = stub.CountObjectVideo(service.ObjectRequest(ws="/home/datdt/Downloads/video/Object_sign.mp4"))
box = service.Box(x=300,y=200,width=400,height=500)
areas = service.Area(area_id='1', detection_area=box)
metadata = [('api_key', 'SuMSTOeJueE0vp6p3mgR1K3TrrDh26Ow2')]
response = stub.ViolateObjectDetect(service.ObjectRequest(ws="rtsp://admin:abcd1234@172.16.10.84:554/Channels/101", areas=[areas]), metadata=metadata)
# request = service.StreamingRequest(source_url="rtsp://admin:abcd1234@172.16.10.84:554/Channels/101")
# results = stub.DetectFire(request)
for result in response:
    # for i, _ in enumerate(result.name):
    #     print(result.name[i], " ", result.count[i])
    print("Timestamp: ", result.timestamp)
    for Object in result.counted_Objects:
        for detail in Object.detail:
            print("Object: ", detail.Object_type , " has ", detail.count)



# import requests
# import json
#
# def sendSMS(msg,numbers):
#     headers = {
#     "authkey": "place AUTH-KEY here",
#     "Content-Type": "application/json"
#     }
#
#     data = "{ \"sender\": \"GTURES\", \"route\": \"4\", \"country\": \"91\", \"sms\": [ { \"message\": \""+msg+"\", \"to\": "+json.dumps(numbers)+" } ] }"
#
#     requests.post("https://api.msg91.com/api/v2/sendsms", headers=headers, data=data)
# sendSMS("hi, i'm detdet",[+84966250499])
