from concurrent import futures

import grpc
from werkzeug.security import check_password_hash, generate_password_hash

import service_pb2
import service_pb2_grpc
from app.models.user import User, db
from app.utils.jwt_util import generate_jwt


class UserService(service_pb2_grpc.UserServiceServicer):
    def Register(self, request, context):
        username = request.username.strip()
        email = request.email.strip()
        password = request.password

        if not username or not email or not password:
            return service_pb2.UserResponse(
                success=False, message="Username, email, and password cannot be empty"
            )

        hashed_password = generate_password_hash(password)

        try:
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            if existing_user:
                return service_pb2.UserResponse(
                    success=False, message="Username or email already exists"
                )

            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return service_pb2.UserResponse(
                success=True, message="User registered successfully"
            )
        except Exception as e:
            db.session.rollback()
            return service_pb2.UserResponse(
                success=False, message=f"Database error: {str(e)}"
            )
        finally:
            db.session.remove()

    def Login(self, request, context):
        email = request.email.strip()
        password = request.password

        if not email or not password:
            return service_pb2.LoginResponse(
                success=False, token="Email and password cannot be empty"
            )

        try:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                token = generate_jwt(user.id)
                return service_pb2.LoginResponse(success=True, token=token)
            return service_pb2.LoginResponse(success=False, token="Invalid credentials")
        except Exception as e:
            return service_pb2.LoginResponse(
                success=False, token=f"Database error: {str(e)}"
            )
        finally:
            db.session.remove()


def create_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:50051")
    return server
