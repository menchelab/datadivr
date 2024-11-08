from datadivr.utils.messages import Message, create_error_message


async def sum_handler(message: Message) -> Message:
    try:
        numbers = message.payload["numbers"]
        if not isinstance(numbers, list):
            return create_error_message("Payload must be a list of numbers", message.from_id)

        result = sum(float(n) for n in numbers)
        return Message(
            event_name="sum_handler_result",
            payload=result,
            to=message.from_id,  # only tell the sender the result, in case we wanted to share it with everybody we put "others" here, or "all" to have it sent to ourself too
        )
    except Exception as e:
        return create_error_message(f"Error: {e!s}", message.from_id)
