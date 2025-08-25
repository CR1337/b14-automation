import requests
import urllib3
import ssl
import platform

match platform.system():
    case "Windows":
        def get_from_url(**kwargs) -> requests.Response:  # type: ignore
            '''
            Windows version
            '''
            kwargs["verify"] = False
            return requests.get(**kwargs)
        
    case _:
        def get_from_url(**kwargs) -> requests.Response:
            '''
            Linux version
            https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled/71646353#71646353
            '''
            class CustomHttpAdapter(requests.adapters.HTTPAdapter):  # type: ignore
                # "Transport adapter" that allows us to use custom ssl_context.

                def __init__(self, ssl_context=None, **kwargs):
                    self.ssl_context = ssl_context
                    super().__init__(**kwargs)

                def init_poolmanager(self, connections, maxsize, block=False):
                    self.poolmanager = urllib3.poolmanager.PoolManager(
                        num_pools=connections, maxsize=maxsize,
                        block=block, ssl_context=self.ssl_context)

            def get_legacy_session() -> requests.Session:
                ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
                session = requests.session()
                session.mount('https://', CustomHttpAdapter(ctx))
                return session

            return get_legacy_session().get(**kwargs)