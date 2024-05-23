import json
import logging
import pathlib
import time

import boto3
import picollm

from http import HTTPStatus

from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

ACCESS_KEY = "{YOUR_ACCESS_KEY_HERE}"

pllm = None


def load_picollm(connection_id, apigw_client):
    global pllm

    if pllm is None:
        send_message(
            {"action": "info", "msg": "Lambda is loading & caching picoLLM. Please wait..."},
            connection_id,
            apigw_client)
        model_path = str(next(pathlib.Path('/').glob('*.pllm')))
        pllm = picollm.create(
            access_key=ACCESS_KEY,
            model_path=model_path,
            device='cpu:5')


def send_message(payload, connection_id, apigw_client):
    response = apigw_client.post_to_connection(Data=json.dumps(payload), ConnectionId=connection_id)
    logger.info(f"Posted message `{json.dumps(payload)}` to connection `{connection_id}`")
    logger.info(f"Response `{response}`")


def handle_message(prompt, connection_id, apigw_client):
    try:
        load_picollm(connection_id, apigw_client)
    except Exception as e:
        send_message(
            {"action": "error", "msg": f"Failed to initialize picoLLM: {e}"},
            connection_id,
            apigw_client)
        return HTTPStatus.INTERNAL_SERVER_ERROR

    start_sec = [0.]

    def stream_callback(token: str):
        if start_sec[0] == 0.:
            start_sec[0] = time.time()
        send_message({"action": "completion", "msg": token}, connection_id, apigw_client)

    send_message({"action": "completion-start"}, connection_id, apigw_client)
    try:
        res = pllm.generate(
            prompt,
            completion_token_limit=256,
            presence_penalty=3,
            frequency_penalty=0,
            temperature=0.7,
            top_p=0.6,
            stream_callback=stream_callback)
    except Exception as e:
        send_message(
            {"action": "error", "msg": f"Failed to generate: {e}"},
            connection_id,
            apigw_client)
        return HTTPStatus.INTERNAL_SERVER_ERROR

    tps = (res.usage.completion_tokens - 1) / (time.time() - start_sec[0])

    send_message(
        {"action": "completion-finish", "tps": tps, "completion": res.completion},
        connection_id,
        apigw_client)

    return HTTPStatus.OK


def handler(event, context):
    route_key = event.get("requestContext", {}).get("routeKey")
    connection_id = event.get("requestContext", {}).get("connectionId")
    if route_key is None or connection_id is None:
        return {"statusCode": HTTPStatus.BAD_REQUEST}

    domain = event.get("requestContext", {}).get("domainName")
    stage = event.get("requestContext", {}).get("stage")
    if domain is None or stage is None:
        return {"statusCode": HTTPStatus.BAD_REQUEST}

    apigw_client = boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{domain}/{stage}")

    response = {"statusCode": HTTPStatus.OK}

    if route_key == "$connect":
        response["statusCode"] = HTTPStatus.OK

    elif route_key == "$disconnect":
        response["statusCode"] = HTTPStatus.OK

    elif route_key == "sendmessage":
        body = event.get("body")
        if body is None:
            response["statusCode"] = HTTPStatus.BAD_REQUEST
            return response

        body = json.loads(body)
        if body.get("prompt") is None:
            response["statusCode"] = HTTPStatus.BAD_REQUEST
            return response

        response["statusCode"] = handle_message(body["prompt"], connection_id, apigw_client)

    else:
        response["statusCode"] = HTTPStatus.NOT_FOUND

    return response
