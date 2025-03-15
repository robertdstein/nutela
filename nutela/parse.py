"""
Parse GCN messages
"""
from nutela.notice import AstrotrackNotice


def parse_gcn_notice(message) -> AstrotrackNotice:
    """Parse GCN message."""
    # Parse the message
    message = message.value()
    # Parse the message
    message = message.decode('utf-8')
    message = message.split('\n')
    message = [line.split(':') for line in message]
    message = {line[0].lower(): ":".join(line[1:]).strip() for line in message if line[0] != ''}
    # Return the message
    return AstrotrackNotice(**message)