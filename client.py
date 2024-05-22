import json
import picollm

from argparse import ArgumentParser

from websockets.sync.client import connect


def handle_message(message):
    message = json.loads(message)
    message['action'] = message.get('action', "")

    if ("info" == message['action']):
        print(f"< [{message['msg']}]")
        return False, None

    elif("completion-start" == message['action']):
        print(f"<", end='', flush=True)
        return False, None

    elif("completion" == message['action']):
        text = message['msg'].removesuffix("<|endoftext|>")
        print(text, end='', flush=True)
        return False, None

    elif("completion-finish" == message['action']):
        tps = message['tps']
        print("")
        print(f"< [Completion finished @ `{tps:.2f}` tps]\n")
        return True, message['completion']

    return False, None


def chat(websocket):
    dialog = picollm.Phi2ChatDialog(history=3)

    while True:
        prompt = input("> ")
        dialog.add_human_request(prompt)
        payload = {
            "action": "sendmessage",
            "prompt": dialog.prompt()
        }
        websocket.send(json.dumps(payload))

        completion = None
        finished = False
        while not finished:
            message = websocket.recv()
            finished, completion = handle_message(message)

        if completion is not None:
            dialog.add_llm_response(completion)


def main():
    parser = ArgumentParser()

    parser.add_argument(
        '--url',
        '-u',
        required=True)
    args = parser.parse_args()

    with connect(args.url) as websocket:
        chat(websocket)


if __name__ == '__main__':
    main()
