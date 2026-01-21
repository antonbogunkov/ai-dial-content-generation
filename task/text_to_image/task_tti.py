import asyncio
from datetime import datetime

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    # TODO:
    #  1. Create DIAL bucket client
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as client:
        #  2. Iterate through Images from attachments, download them and then save here
        for attachment in attachments:
            file_content = await client.get_file(url=attachment.url)
            file_name = f'{attachment.title}.{attachment.type.split('/')[-1]}'
            with open(file_name, 'wb') as file:
                file.write(file_content)
            #  3. Print confirmation that image has been saved locally
            print('File received: ', file_content)


models = [
    # 'gpt-4o',
    # 'gemini-2.0-flash-lite',
    # 'anthropic.claude-v3-haiku',
    'imagegeneration@005',
]


def start() -> None:
    model_name = models[0]

    user_input = input('User says: ')

    custom_fields = {   # FIXME: raises error extra is not allowed
        # 'size': Size.width_rectangle,
        # 'style': Style.natural,
        # 'quality': Quality.hd,
    }
    
    #  1. Create DialModelClient
    client = DialModelClient(endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT, api_key=API_KEY, deployment_name=model_name)
    #  2. Generate image for "Sunny day on Bali"
    response = client.get_completion(messages=[Message(role=Role.USER, content=user_input or 'Sunny day on Bali')], custom_fields=custom_fields)
    attachments = response.custom_content.attachments
    print(attachments)
    #  3. Get attachments from response and save generated message (use method `_save_images`)
    asyncio.run(_save_images(attachments=attachments))
    #  4. Try to configure the picture for output via `custom_fields` parameter.
    #    - Documentation: See `custom_fields`. https://dialx.ai/dial_api#operation/sendChatCompletionRequest
    #  5. Test it with the 'imagegeneration@005' (Google image generation model)


start()
