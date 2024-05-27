# Serverless picoLLM: LLMs Running in AWS Lambda!

Code for the Serverless LLM article on picovoice.ai which you can find here: [picoLLM on Lambda](https://picovoice.ai/blog/picollm-on-lambda/).

![The Demo in Action](resources/serverless-picollm-small.gif)

## Disclaimer

THIS DEMO EXCEEDS *AWS* FREE TIER USAGE.
YOU **WILL** BE CHARGED BY *AWS* IF YOU DEPLOY THIS DEMO.

## Prerequisites

You will need to following in order to deploy and run this demo:

1. A [Picovoice Console](https://console.picovoice.ai/) account with a valid AccessKey.

2. An [AWS](https://aws.amazon.com/) account.

3. AWS SAM CLI installed and setup. Follow the [offical guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) completely.

4. A valid [Docker](https://docs.docker.com/get-docker/) installation.

## Setup

1. Clone the [`serverless-picollm` repo](https://github.com/Picovoice/serverless-picollm):

```console
git clone https://github.com/Picovoice/serverless-picollm.git
```

2. Download a `Phi2` based `.pllm` model from the `picoLLM` section of the [Picovoice Console](https://console.picovoice.ai/picollm).

> [!TIP]
> Other models will work as long as they are chat-enabled and fit within the AWS Lambda code size and memory limits.
> You will also need to update the `Dialog` object in [client.py](client.py) to the appropriate class.

3. Place the downloaded `.pllm` model in the [`models/`](models/) directory.

4. Replace `"${YOUR_ACCESS_KEY_HERE}"` inside the [`src/app.py`](src/app.py) file with your AccessKey obtained from [Picovoice Console](https://console.picovoice.ai/).

## Deploy

1. Use AWS SAM CLI to build the app:

```console
sam build
```

2. Use AWS SAM CLI to deploy the app, following the guided prompts:

```console
sam deploy --guided
```

3. At the end of the deployment AWS SAM CLI will print an outputs section. Make note of the `WebSocketURI`. It should look something like this:

```
CloudFormation outputs from deployed stack
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Outputs
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Key                 HandlerFunctionFunctionArn
Description         HandlerFunction function ARN
Value               arn:aws:lambda:us-west-2:000000000000:function:picollm-lambda-HandlerFunction-ABC123DEF098

Key                 WebSocketURI
Description         The WSS Protocol URI to connect to
Value               wss://ABC123DEF098.execute-api.us-west-2.amazonaws.com/Prod
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

```
wss://ABC123DEF098.execute-api.us-west-2.amazonaws.com/Prod
```
> [!NOTE]
> If you make any changes to the model, `Dockerfile` or `app.py` files, you will need to repeat all these deployment steps.

## Chat!

1. Run `client.py`, passing in the URL copied from the deployment step:

```console
python client.py -u <WebSocket URL>
```

2. Once connected the client will give you a prompt. Type in your chat message and `picoLLM` will stream back a response from the lambda!

```
> What is the capital of France?
< The capital of France is Paris.

< [Completion finished @ `6.35` tps]
```

> [!IMPORTANT]
> When you first send a message you may get the following response: `< [Lambda is loading & caching picoLLM. Please wait...]`.
> This means the `picoLLM` is loading the model as lambda streams it from the Elastic Container Registry.
> Because of the nature and limitations of AWS Lambda this process *may* take upwards of a few minutes.
> Subsequent messages and connections will not take as long to load as lambda will cache the layers.
