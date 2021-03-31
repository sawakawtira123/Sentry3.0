import uvicorn
from sentry.settings import setting


uvicorn.run('sentry.app:app',
            host=setting.server_host,
            port=setting.server_port,
            reload=True
            )
