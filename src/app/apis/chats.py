from app.utils.Apierros import AppError
from app.utils.database import db
from app.utils.pydanticTypes.Chat.types import ChatApiResponse


async def get_chat_by_id(chat_id: int, cursor: int, data, limit):

    parsed_cursor = cursor if cursor else None
    query = """
    SELECT
        m.id,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN 'Deleted Message'
            ELSE m.content
        END AS content,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN NULL
            ELSE a.url
        END AS preview,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN NULL
            ELSE m.story_id
        END AS story_id,

        m.chat_id,
        m.sender_id,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN NULL
            ELSE st.content
        END AS story_item,

        m.created_at,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN FALSE
            ELSE m.is_forwarded
        END AS is_forwarded,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN FALSE
            ELSE m.is_edited
        END AS is_edited,

        m.is_deleted,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN NULL
            ELSE m.reply_to_message_id
        END AS reply_to_message_id,

        COALESCE(seen.seen_users, '{}') AS seen_users,

        CASE
            WHEN md.message_id = m.id
                AND md.user_id = $1
            THEN '[]'::json
            ELSE COALESCE(r.reactions, '[]'::json)
        END AS reactions

    FROM message m

    LEFT JOIN LATERAL (
        SELECT ARRAY_AGG(sm.user_id) AS seen_users
        FROM seen_message sm
        WHERE sm.message_id = m.id
    ) seen ON TRUE

    LEFT JOIN story st
        ON st.id = m.story_id

    LEFT JOIN message_delete_for_me md
        ON m.id = md.message_id
        AND md.user_id = $1

    LEFT JOIN attachment a
        ON a.message_id = m.id

    LEFT JOIN LATERAL (
        SELECT json_agg(
            json_build_object(
                'react_id', mr.reaction_id,
                'user_id', ru.id
            )
        ) AS reactions

        FROM message_reaction mr

        JOIN users ru
            ON ru.id = mr.user_id

        WHERE mr.message_id = m.id
    ) r ON TRUE

    WHERE
        m.chat_id = $2

        AND m.is_deleted = FALSE

        AND NOT EXISTS (
            SELECT 1
            FROM block b

            WHERE
                (
                    (
                        b.user_id = $1
                        AND b.blocked_user_id = m.sender_id
                    )
                    OR
                    (
                        b.user_id = m.sender_id
                        AND b.blocked_user_id = $1
                    )
                )

                AND m.created_at >= b.blocked_at

                AND (
                    b.unblocked_at IS NULL
                    OR m.created_at <= b.unblocked_at
                )
        )
"""

    params = [data["id"], chat_id]

    if cursor:
        query += """
            AND m.id < $3
        """
        params.append(parsed_cursor)

    query += (
        """
        ORDER BY m.id DESC
        LIMIT $4
    """
        if cursor
        else """
        ORDER BY m.id DESC
        LIMIT $3
    """
    )
    params.append(limit)

    chats = await db.query_raw(query, *params)
    formatted_chat = chats[::-1]

    next_cursor = chats[-1]["id"] if chats else None

    return ChatApiResponse(
        message="Successfully Retrieved Messages",
        status=200,
        data={
            "items": formatted_chat,
            "next_cursor": next_cursor,
            "has_more": len(chats) == limit,
        },
    )


async def create_chat(member_id: int, data):
    if not member_id:
        raise AppError(message="Member id is missing", status=400, success=False)

    if data["id"] == member_id:
        raise AppError(
            message="You can not create chat with yourself",
            status=400,
            success=False,
        )

    existing_user = await db.query_raw(
        """
                                       select * from users where id = $1 and account_status = 'active'::account_status
                                       """,
        member_id,
    )

    if len(existing_user) == 0:
        raise AppError(
            message="User not Exists or Account may be deleted",
            status=400,
            success=False,
        )
    member_ids = sorted([data["id"], member_id])
    exists = await db.query_raw(
        """
                            select chat_id from chat_member GROUP BY chat_id
                            HAVING 
                            ARRAY_AGG(DISTINCT member_id ORDER BY member_id) = $1::integer[]
                            """,
        member_ids,
    )
    if len(exists) >= 1:
        raise AppError(
            message="Chat ALready Exixts with this user", status=400, success=False
        )
    new_chat = await db.query_raw("""
                                  
                                  insert into chat (chat_type) values('private') returning *
                                  """)

    members = await db.chat_member.create_many(
        data=[
            {
                "member_id": member_id,
                "chat_id": new_chat[0]["id"],
            }
            for member_id in [data["id"], member_id]
        ]
    )

    return ChatApiResponse(
        message="Successfully Created New chat", status=201, success=True
    )
