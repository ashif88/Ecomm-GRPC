import grpc
import service_pb2
import service_pb2_grpc
from concurrent import futures
from app.utils.kafka_producer import send_message

class NotificationService(service_pb2_grpc.NotificationServiceServicer):
    def SendEmail(self, request, context):
        subject = request.subject
        body = request.body
        recipient = request.recipient

        send_message('email_topic', f"To: {recipient}, Subject: {subject}, Body: {body}")

        return service_pb2.NotificationResponse(success=True, message="Email sent successfully")

def create_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_NotificationServiceServicer_to_server(NotificationService(), server)
    server.add_insecure_port('[::]:50054')
    return server
