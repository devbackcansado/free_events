SELECT
    COUNT(1) OVER() AS total,
    ee.uid,
    ee.title,
    ee.description,
    ee.address,
    ee.start_at,
    ee.is_active,
    ee.created_at,
    ee.updated_at,
    COALESCE(
    JSONB_AGG(
        JSONB_BUILD_OBJECT(
            'uid', es.uid,
            'email', au.email,
            'status',
            CASE
                WHEN ess.status = 1 THEN 'Criado'
                WHEN ess.status = 2 THEN 'Confirmado'
                WHEN ess.status = 3 THEN 'Cancelado'
                WHEN ess.status = 4 THEN 'Desinscrito'
                ELSE 'Desconhecido'
            END
        )
    ) FILTER (WHERE es.uid IS NOT NULL),
    '[]'::jsonb
) AS list_subscriptions
FROM
    events_event ee
LEFT JOIN
    events_subscription es ON ee.id = es.event_id
LEFT JOIN
    accounts_user au ON es.user_id = au.id
LEFT JOIN LATERAL (
    SELECT
        ess.status
    FROM
        events_subscriptionstatus ess
    WHERE
        ess.subscription_id = es.id
    ORDER BY
        ess.created_at DESC
    LIMIT 1
) ess ON true
GROUP BY
    ee.id
ORDER BY
    ee.start_at ASC
LIMIT %s
OFFSET %s;
