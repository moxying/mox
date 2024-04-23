import uvicorn


# FastAPI Uvicorn override, see: https://github.com/encode/uvicorn/issues/1579
class UvicornServer(uvicorn.Server):

    # Override
    def install_signal_handlers(self) -> None:

        # Do nothing
        pass
