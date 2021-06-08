from concurrent import futures
import grpc
from models.experimental import attempt_load
from utils import config
from tracker.sort import Sort
from detector import violate_object_detect
from protos import object_server_pb2 as service
from protos import object_server_pb2_grpc
from utils.torch_utils import select_device
from utils.logging import setup_logging_json
import logging
from protos.object_server_pb2 import (
    CountObjectResponse
)

LOGGER = logging.getLogger(__name__)
def get_api_key(context) -> str:
    """
    Get api_key in metadata, raise error if does not exist
    Args:
        context: gRPC context
    Returns:
        api_key: (str) key to use API
    """
    provided_api_key = ""
    for key, value in context.invocation_metadata():
        if key == "api_key":
            provided_api_key = str(value)
            return provided_api_key
    return provided_api_key

class Object:
  def __init__(self, name, bbox, time_arrival):
    self.name = name
    self.bbox = bbox
    self.time_arrival = time_arrival

def counted_Objects_byarea(countedObjects, area_id, total_Object):
    """
    Convert db Object to gRPC Object_metadata
    :params Object: Object
    :returns Object_metadata: service.ObjectMetadata
    """
    Object_metadata = service.CountedObjectsByArea(
        area_id=area_id,
        total_Object=total_Object,
        detail=countedObjects)
    return Object_metadata

def counted_Objects(count, Object_type):
    """
    Convert db Face to gRPC _metadata
    :params Object: Object
    :returns Object_metadata: service.ObjectMetadata
    """
    countedObjects = service.CountedObjects(
        count=count,
        Object_type=Object_type,
        )

    return countedObjects

class ObjectService(object_server_pb2_grpc.ObjectServiceServicer):

    def ViolateObjectDetect(self, request, context):
        if request.ws is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "WebSocket not found")
            LOGGER.error("WebSocket not found")
        try:
            url = request.ws
            LOGGER.info("Reading data from url: {}".format(url))
            tracker = Sort()
            areas = request.areas
            api_key = get_api_key(context)
            print('API key:', api_key)
            Objects = violate_object_detect(model, url, image_size, iou_thres, conf_thres, device, tracker, areas)
            for name_Object, count, timestamp, bounding_boxes, trackers in Objects:
                counted_Object = []
                yield CountObjectResponse(counted_Objects=counted_Object, timestamp=timestamp)
        except Exception as e:
            LOGGER.error(e)
            return CountObjectResponse()

def serve():
    # Initialize server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    object_server_pb2_grpc.add_ObjectServiceServicer_to_server(
        ObjectService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    setup_logging_json("logging.json")
    weights = config.get_model()
    image_size = int(config.get_image_size())
    iou_thres = float(config.get_iou_threshold())
    conf_thres = float(config.get_confidence_threshold())
    # get device from file config
    device = config.get_divice()
    # Select device add to torch
    device = select_device(device=device)
    half = device.type != 'cpu'  # half precision only supported on CUDA
    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride

    serve()
