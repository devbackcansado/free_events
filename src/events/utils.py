FIELDS_BY_EVENT_MODEL_DUMP = (
    "uid",
    "promoter__email",
    "title",
    "description",
    "address",
    "start_at",
    "is_active",
    "created_at",
    "updated_at",
)

FIELDS_BY_SUBSCRIPTION_MODEL_DUMP = (
    "uid",
    "event__title",
    "event__description",
    "event__address",
    "event__start_at",
    "event__is_active",
    "created_at",
    "updated_at",
)


FIELDS_SUBSCRIPTION_BY_DASHBOARD_DUMP = (
    "uid",
    # "user__email",
    # "created_at",
    # "updated_at",
    "status",
)
