import json
import os

import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from google.cloud.firestore_v1 import AsyncClient


class FirebaseManager:
    _apps = {}
    _clients = {}

    @classmethod
    def init(cls, service_account: dict, name: str) -> firebase_admin.App:
        """Initialize Firebase app by name."""
        if name not in cls._apps:
            try:
                cls._apps[name] = firebase_admin.get_app(name)
            except ValueError:
                creds = service_account['credentials']
                cred_data = (
                    creds
                    if isinstance(creds, dict)
                    else json.load(open(creds))
                    if os.path.exists(creds)
                    else json.loads(creds)
                )

                cred = credentials.Certificate(cred_data)
                storage_bucket = service_account.get('storage')
                cls._apps[name] = firebase_admin.initialize_app(
                    cred, {"storageBucket": storage_bucket}, name=name
                )
        return cls._apps[name]

    @classmethod
    async def get_db(cls, name: str, service_account: dict = None) -> AsyncClient:
        """Get or create async Firestore client for specific app."""
        if name not in cls._clients:
            if name not in cls._apps:
                if not service_account:
                    raise RuntimeError(f"App {name} not initialized")
                cls.init(service_account, name)

            app = cls._apps[name]
            cls._clients[name] = firestore.AsyncClient(
                credentials=app.credential.get_credential(),
                project=app.project_id,
            )
        return cls._clients[name]
