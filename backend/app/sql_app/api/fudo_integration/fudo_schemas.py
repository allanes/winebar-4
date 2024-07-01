from typing import Optional, List, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class TableAttributes(BaseModel):
    column: int
    number: int
    row: int
    shape: str
    size: str

class RoomData(BaseModel):
    type: str
    id: str

class SaleData(BaseModel):
    type: str   
    id: str

class TableRelationships(BaseModel):
    room: dict[str, RoomData]
    activeSales: dict[str, List[SaleData]]

class Table(BaseModel):
    type: str
    id: str
    attributes: TableAttributes
    relationships: TableRelationships

class SaleAttributes(BaseModel):
    closedAt: Optional[datetime]
    comment: Optional[str]
    createdAt: datetime
    people: int
    customerName: Optional[str]
    total: float
    saleType: str
    saleState: str

class RelationshipData(BaseModel):
    type: Optional[str]
    id: Optional[str]

class SaleRelationships(BaseModel):
    customer: dict[str, Optional[RelationshipData]]
    discounts: dict[str, List[Any]]
    items: dict[str, List[RelationshipData]]
    payments: dict[str, List[Any]]
    tips: dict[str, List[Any]]
    shippingCosts: dict[str, List[Any]]
    table: dict[str, RelationshipData]
    waiter: dict[str, Optional[RelationshipData]]
    saleIdentifier: dict[str, Optional[RelationshipData]]

class Sale(BaseModel):
    type: str
    id: str
    attributes: SaleAttributes
    relationships: SaleRelationships

class TablesResponse(BaseModel):
    data: List[Table]
    included: Optional[List[Sale]] = None

class SaleResponse(BaseModel):
    data: Sale

class CustomSaleDetailResponse(BaseModel):
    id: str
    type: str

    # closedAt: Optional[datetime]
    # comment: Optional[str]
    # saleType: str
    createdAt: datetime
    people: int
    customerName: Optional[str]
    total: str
    saleState: str

class MesaFudoCustom(BaseModel):
    id: int
    number: int
    room_id: str
    room_name: Optional[str] = 'Hab.'
    cant_ventas: int
    activeSales: dict[str, List[SaleData]]

class CustomTableResponse(BaseModel):
    data: List[MesaFudoCustom]

class RoomAttr(BaseModel):
    name: str

class SingleRoomDetails(BaseModel):
    id: int
    type: str
    attributes: RoomAttr
    
class RoomsResponse(BaseModel):
    data: List[SingleRoomDetails]
    
class FudoItemType(str, Enum):
    TAPA = "TAPA"
    VINO = "VINO"

class FudoExportItem(BaseModel):
    order_id: int
    type: FudoItemType
    amount: float
    quantity: int
    comment: str
    sale_id: str

class FudoExportRequest(BaseModel):
    items: List[FudoExportItem]

class FudoItemPayload(BaseModel):
    data: dict

FUDO_PRODUCT_IDS = {
    FudoItemType.TAPA: "121",
    FudoItemType.VINO: "342"
}

FUDO_ITEM_CREATE__MOCK_RESPONSE = {
    "data": {
        "type": "Item",
        "id": "434",
        "attributes": {
            "canceled": None,
            "cancellationComment": None,
            "comment": "Exportado desde App",
            "createdAt": "2024-06-30T20:08:31Z",
            "price": 111,
            "quantity": 22,
            "status": "PENDING"
        },
        "relationships": {
            "priceList": {
                "data": {
                "type": "PriceList",
                "id": "1"
                }
            },
            "product": {
                "data": {
                "type": "Product",
                "id": "342"
                }
            },
            "subitems": {
                "data": []
            },
            "sale": {
                "data": {
                "type": "Sale",
                "id": "248"
                }
            }
        }
    }
}