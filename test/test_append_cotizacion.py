import datetime
from iol_sheets.sheet_client import SheetClient, Scope
from iol_client.client import IOLClient
from iol_client.constants import Mercado, Plazo
import pytest
import os


class MockIOLClient(IOLClient):
    def __init__(self) -> None:
        self.was_called = False

    async def get_titulo_cotizacion_plazo(
        self, simbolo: str, mercado: Mercado, plazo: Plazo
    ):
        self.was_called = True
        return {
            "operableCompra": True,
            "operableVenta": False,
            "visible": True,
            "ultimoPrecio": 123.0,
            "variacion": 123.0,
            "apertura": 123.0,
            "maximo": 123.0,
            "minimo": 123.0,
            "fechaHora": datetime.datetime.now(),
            "tendencia": "sube",
            "cierreAnterior": 123.0,
            "montoOperado": 123.0,
            "volumenNominal": 123.0,
            "precioPromedio": 123,
            "moneda": "peso_Argentino",
            "precioAjuste": 0.0,
            "interesesAbiertos": 0.0,
            "puntas": [
                {
                    "cantidadCompra": 1,
                    "precioCompra": 2,
                    "precioVenta": 3,
                    "cantidadVenta": 4,
                }
            ],
            "cantidadOperaciones": 123,
            "simbolo": "GGAL",
            "pais": "Argentina",
            "mercado": "BCBA",
            "tipo": "ACCIONES",
            "descripcionTitulo": "Grupo Financiero Galicia",
            "plazo": "T0",
            "laminaMinima": 123,
            "lote": 123,
            "cantidadMinima": 123,
            "puntosVariacion": 123,
        }


@pytest.mark.asyncio
async def test_append_a_cotizacion_mock():
    mock_iol = MockIOLClient()
    sheet_client = SheetClient(
        spreadsheet_id=os.getenv("SPREADSHEET_ID") or "",
        credentials_file=os.getenv("CREDENTIALS_FILE_JSON") or "",
        iol_api=mock_iol,
        scopes=[Scope.WRITEABLE],
    )

    res = await sheet_client.append_cotizacion_titulo(
        simbolo="GGAL",
        mercado=Mercado.BCBA,
        plazo=Plazo.T0,
    )

    assert mock_iol.was_called
    assert res.get("updates").get("updatedCells") == 32


@pytest.mark.asyncio
async def test_append_a_cotizacion_real():
    mock_iol = IOLClient(
        username=os.getenv("IOL_USER") or "",
        password=os.getenv("IOL_PASS") or "",
    )
    sheet_client = SheetClient(
        spreadsheet_id=os.getenv("SPREADSHEET_ID") or "",
        credentials_file=os.getenv("CREDENTIALS_FILE_JSON") or "",
        iol_api=mock_iol,
        scopes=[Scope.WRITEABLE],
    )

    res = await sheet_client.append_cotizacion_titulo(
        simbolo="GGAL",
        mercado=Mercado.BCBA,
        plazo=Plazo.T0,
    )

    assert res.get("updates").get("updatedCells") >= 32
