import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image(file_name: str) -> Attachment:
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'

    #  1. Create DialBucketClient
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as client:
        #  2. Open image file
        with open(image_path, 'rb') as image:
            #  3. Use BytesIO to load bytes of image
            img_bytes = BytesIO(image.read())
        #  4. Upload file with client
        response_data = await client.put_file(name=file_name, mime_type=mime_type_png, content=img_bytes)
        #  5. Return Attachment object with title (file name), url and type (mime type)
        return Attachment(title=file_name, url=response_data.get('url'), type=mime_type_png)


models = [
    'gpt-4o',
    'gemini-2.0-flash-lite',
    'anthropic.claude-v3-haiku',
]


def start() -> None:
    try:
        model_name = models[int(input('Select a model to use [0-2]: '))]
    except (ValueError, IndexError):
        raise Exception('Wrong model index provided.')
    
    #  1. Create DialModelClient
    client = DialModelClient(endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT, deployment_name=model_name, api_key=API_KEY)
    #  2. Upload image (use `_put_image` method )
    attachment1 = asyncio.run(_put_image(file_name='dialx-banner.png'))
    attachment2 = asyncio.run(_put_image(file_name='Elephant-male-1024x535.jpg'))
    #  3. Print attachment to see result
    print(attachment1, attachment2)
    #  4. Call chat completion via client with list containing one Message:
    response = client.get_completion(
        messages=[Message(
            #    - role: Role.USER
            role=Role.USER,
            #    - content: "What do you see on this picture?"
            content='What do you see on this picture?',
            #    - custom_content: CustomContent(attachments=[attachment])
            custom_content=CustomContent(attachments=[attachment1, attachment2]),
        )]
    )
    print(response)
    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis


start()
