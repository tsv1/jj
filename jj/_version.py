import aiohttp

version = "2.0.0"
server_version = "jj/{} via aiohttp/{}".format(version, aiohttp.__version__)


__all__ = ("version", "server_version")
