import grpc
from app.utils.jwt_util import decode_jwt

class AuthInterceptor(grpc.ServerInterceptor):
    def __init__(self, protected_methods):
        self.protected_methods = protected_methods

    def intercept_service(self, continuation, handler_call_details):
        method_name = handler_call_details.method
        if method_name in self.protected_methods:
            metadata = dict(handler_call_details.invocation_metadata)
            auth_header = metadata.get('authorization')
            print(f"Auth interceptor: method={method_name}, auth_header={auth_header[:20] if auth_header else None}")
            if not auth_header or not auth_header.startswith('Bearer '):
                print("Missing or invalid token prefix")
                return self._abort(grpc.StatusCode.UNAUTHENTICATED, "Missing or invalid token")
            
            token = auth_header.split(' ')[1]
            user_id = decode_jwt(token)
            print(f"Decoded user_id: {user_id}")
            if user_id is None: # Explicitly check for None
                print("Token invalid or expired")
                return self._abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or expired token")
            
        return continuation(handler_call_details)

    def _abort(self, code, details):
        def abort_handler(request, context):
            context.abort(code, details)
        return grpc.unary_unary_rpc_method_handler(abort_handler)
