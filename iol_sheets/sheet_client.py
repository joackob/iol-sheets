from __future__ import print_function
from enum import Enum

from .logger import Logger
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from iol_client.client import IOLClient
from iol_client.constants import Mercado, Plazo
from google.oauth2 import service_account
import pandas as pd
import os


class Scope(Enum):
    def __str__(self) -> str:
        return self.value

    READONLY = "https://www.googleapis.com/auth/spreadsheets.readonly"
    WRITEABLE = "https://www.googleapis.com/auth/spreadsheets"


# to be deprecated
def flat_cotizacion(cotizacion):
    cant_puntas = len(cotizacion["puntas"])


class SheetClient:
    def __init__(
        self,
        spreadsheet_id: str,
        token_file: str,
        credentials_file: str,
        iol_api: IOLClient,
        scopes: list[Scope] = [Scope.READONLY],
    ):
        self.logger = Logger(__name__)
        self.spreadsheet_id = spreadsheet_id
        self.iol_api = iol_api
        self.creds = None

        # if os.path.exists(token_file):
        #     self.creds = Credentials.from_authorized_user_file(
        #         filename=token_file, scopes=map(str, scopes)
        #     )

        # if not self.creds or not self.creds.valid:
        #     if self.creds and self.creds.expired and self.creds.refresh_token:
        #         self.creds.refresh(Request())
        #     else:
        #         flow = InstalledAppFlow.from_client_secrets_file(
        #             credentials_file, scopes=map(str, scopes)
        #         )
        #         self.creds = flow.run_local_server(port=0)
        #     with open(token_file, "w") as token:
        #         token.write(self.creds.to_json())
        if os.path.exists(credentials_file):
            self.creds = service_account.Credentials.from_service_account_file(
                credentials_file, scopes=map(str, scopes)
            )
        else:
            self.logger.error("Credentials file does not exist")
            raise Exception("Credentials file does not exist")

    async def append_cotizacion_titulo(
        self, simbolo: str, mercado: Mercado, plazo: Plazo
    ):
        try:
            cotizacion = await self.iol_api.get_titulo_cotizacion_plazo(
                simbolo=simbolo, mercado=mercado, plazo=plazo
            )
            cotizacion_flatted = [
                {
                    **cotizacion,
                    "puntas": None,
                    "cantidadCompra": punta["cantidadCompra"],
                    "precioCompra": punta["precioCompra"],
                    "precioVenta": punta["precioVenta"],
                    "cantidadVenta": punta["cantidadVenta"],
                }
                for punta in cotizacion["puntas"]
            ]

            df_cotizacion = pd.DataFrame(data=cotizacion_flatted)
            df_cotizacion = df_cotizacion.drop(columns=["puntas"])
            array_cotizacion = df_cotizacion.to_numpy().tolist()

            service = build(serviceName="sheets", version="v4", credentials=self.creds)
            body = {"values": array_cotizacion}
            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"Cotizaciones!A3:F3",
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            self.logger.info(
                f'{result.get("updates").get("updatedCells")} cells appended.'
            )
            return result
        except HttpError as err:
            self.logger.error(err)
            raise err
