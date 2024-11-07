from pydantic import BaseModel, model_validator, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime
from django.db.models import Q
from events.constants import REVERSE_TRANSLATED_SUBSCRIPTION_STATUS


class EventParams(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        ignored_types=(Q,),
        arbitrary_types_allowed=True,
    )
    start_at: datetime = datetime.now()
    limit: Optional[int] = 10
    page: Optional[int] = 1
    order_by: Optional[Literal["start_at", "title"]] = "start_at"
    order: Optional[Literal["asc", "desc"]] = "asc"
    search: Optional[str] = None
    params: Q = Field(default_factory=Q)

    @model_validator(mode="after")
    def check_params(self):
        if self.limit < 1 or self.limit > 100:
            raise ValueError("Limite deve ser entre 1 e 100")

        if self.page < 1:
            raise ValueError("Pagina não pode ser menor que 1")

        if self.order_by not in ["start_at", "title"]:
            raise ValueError("Ordenação inválida")

        if self.order not in ["asc", "desc"]:
            raise ValueError("Ordem inválida")

        if self.search and len(self.search) < 3:
            raise ValueError("Pesquisa deve ter no mínimo 3 caracteres")

        self.order_by = self.order_by if self.order == "asc" else f"-{self.order_by}"
        if self.search:
            self.params &= Q(
                title__icontains=self.search,
                address__icontains=self.search,
            )
        self.params &= Q(start_at__gte=self.start_at)

        return self


class SubscriptionParams(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        ignored_types=(Q,),
        arbitrary_types_allowed=True,
    )
    start_at: datetime = datetime.now()
    status: Optional[Literal["criado", "confirmado", "cancelado", "desinscrito"]] = None
    limit: Optional[int] = 10
    page: Optional[int] = 1
    order_by: Optional[Literal["start_at", "title", "status"]] = "start_at"
    order: Optional[Literal["asc", "desc"]] = "asc"
    search: Optional[str] = None
    params: Q = Field(default_factory=Q)

    @model_validator(mode="after")
    def check_parms(self):
        if self.limit < 1 or self.limit > 100:
            raise ValueError("Limite deve ser entre 1 e 100")

        if self.page < 1:
            raise ValueError("Pagina não pode ser menor que 1")

        if self.order_by not in ["start_at", "title", "status"]:
            raise ValueError("Ordenação inválida")

        if self.order not in ["asc", "desc"]:
            raise ValueError("Ordem inválida")

        if self.search and len(self.search) < 3:
            raise ValueError("Pesquisa deve ter no mínimo 3 caracteres")

        if self.status is not None and self.status.lower() not in ["criado", "confirmado", "cancelado", "desinscrito"]:
            raise ValueError("Status inválido")

        if self.status:
            self.params &= Q(status=REVERSE_TRANSLATED_SUBSCRIPTION_STATUS[self.status.lower()])

        if self.order_by == "status":
            self.order_by = (
                f"subscription_statuses__status" if self.order == "asc" else f"-subscription_statuses__status"
            )
        else:
            self.order_by = f"event__{self.order_by}" if self.order == "asc" else f"-event__{self.order_by}"

        if self.search:
            self.params &= Q(event__title__icontains=self.search, event__address__icontains=self.search)

        self.params &= Q(event__start_at__gte=self.start_at)

        return self
