from flask import Flask, request, Response
from firebase_admin import messaging, credentials, initialize_app
from os import path
import sys
import logging
from constants import TOKEN_PATH, NotificationType, PORT, Language

server = Flask(__name__)


def _base_send(n_type, n_text, tokens):
    if not isinstance(tokens, list):
        tokens = [tokens]
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=n_type, body=n_text),
        data=dict(title=n_type, body=n_type),
        tokens=tokens,
    )
    return messaging.send_multicast(message)


@server.route('/send-notification', methods=['POST'])
def send_notification():
    data = request.json
    try:
        notif_type = NotificationType[data.get('type')].value
    except ValueError:
        return Response(f"{data.get('type')} is unrecognized as notification type", status=404,
                        mimetype='application/json')
    notif_text = data.get('text')
    fib_tokens = data.get('fib_tokens')
    language = data.get('lang')
    if not language:
        language = Language.EN.value
    if not fib_tokens:
        return Response("No FIB tokens provided", status=404, mimetype='application/json')
    response = _base_send(notif_type, notif_text, fib_tokens)
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # repeat up to 3 times
                re_send = False
                for x in range(3):
                    logging.info(f"{x+1}: Retrying sending to token {fib_tokens[idx]}")
                    response = _base_send(notif_type, notif_text, fib_tokens[idx])
                    if not response.failure_count:
                        logging.info(f"Retry send successful")
                        re_send = True
                        break
                if not re_send:
                    logging.info(f"Failed to retry sending")
                    failed_tokens.append(fib_tokens[idx])
        return Response('List of tokens that caused failures: {0}'.format(failed_tokens),
                        status=407,
                        mimetype='application/json')
    return Response(status=200)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    if not path.exists(TOKEN_PATH):
        sys.exit(f"Token file is missing at : {TOKEN_PATH}")
    initialize_app(credentials.Certificate(TOKEN_PATH))
    logging.info("FIB app initialized")
    server.run(host='0.0.0.0', port=PORT)
