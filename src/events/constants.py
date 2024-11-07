from enum import IntEnum


class TypeSubscriptionStatus(IntEnum):
    UNDEFINED = 0
    CREATED = 1
    CONFIRMED = 2
    CANCELED = 3
    UNSIGNED = 4

    @classmethod
    def choices(cls):
        return [
            (cls.CREATED, "Created"),
            (cls.CONFIRMED, "Confirmed"),
            (cls.CANCELED, "Canceled"),
            (cls.UNSIGNED, "Unsigned"),
        ]


TRANSLATED_SUBSCRIPTION_STATUS = {
    TypeSubscriptionStatus.CREATED: "Criado",
    TypeSubscriptionStatus.CONFIRMED: "Confirmado",
    TypeSubscriptionStatus.CANCELED: "Cancelado",
    TypeSubscriptionStatus.UNSIGNED: "Desinscrito",
}

REVERSE_TRANSLATED_SUBSCRIPTION_STATUS = {
    "criado": TypeSubscriptionStatus.CREATED,
    "confirmado": TypeSubscriptionStatus.CONFIRMED,
    "cancelado": TypeSubscriptionStatus.CANCELED,
    "desinscrito": TypeSubscriptionStatus.UNSIGNED,
}
