from planobs.api import Queue

ZTF_USER = "NUTELA"

def get_submitted_too() -> str:
    q = Queue(user=ZTF_USER)
    existing_too_queue = q.get_too_queues_name_and_date()
    message = ""
    for entry in existing_too_queue:
        message += f"{entry}\n"
    message = message[:-1]

    return message


def get_submitted_full() -> str:
    q = Queue(user=ZTF_USER)
    existing_queue = q.get_all_queues_nameonly()
    message = ""
    for entry in existing_queue:
        message += f"{entry}\n"
    message = message[:-1]

    return message


def delete_trigger(triggername) -> None:
    q = Queue(user=ZTF_USER)
    q.delete_trigger(triggername)


def fuzzy_parameters(param_list) -> list:
    """ """
    fuzzy_params = []
    for param in param_list:
        for character in ["", "-", "--", "–"]:
            fuzzy_params.append(f"{character}{param}")
    return fuzzy_params