import os
import chainlit as cl
from groq import Groq
import configparser
from io import BytesIO
import httpx
import whisper
from chainlit.element import ElementBased
from elevenlabs.client import ElevenLabs


# Read the API key
config = configparser.ConfigParser()
config.read(r"weya_takehome/secrets/config.ini")
api_key = config['api']['key']
ELEVENLABS_API_KEY = config['api']['ELEVENLABS_API_KEY']
ELEVENLABS_VOICE_ID = config['id']['Adam']

# Set up a groq client
client = Groq(api_key=api_key)
el_client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY,
)

@cl.step(type="tool")
async def speech_to_text(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]

@cl.step(type="tool")
async def text_to_speech(text: str, mime_type: str):
    # Generate audio using ElevenLabs API
    audio = el_client.generate(
        text=text,
        voice="Adam",
        model='eleven_multilingual_v2'
    )


    # Create a buffer to store the audio
    buffer = BytesIO()
    buffer.name = f"output_audio.{mime_type.split('/')[1]}"

    # Write audio data to buffer
    for chunk in audio:
        buffer.write(chunk)

    buffer.seek(0)

    return buffer.name, buffer.read()
    

@cl.step(type="tool")
async def generate_text_answer(transcription):
    voice_chat_body=''' 
                    Imagine this as a human conversation between a human and a bot. Reply like a human, be short, concise and to the point. Also, try to be polite and not too descriptive unless and until asked to be so. This is the human message: 
                    '''
    transcription = voice_chat_body + transcription
    chat_profile = cl.user_session.get("chat_profile")
    selected_model = profiles[chat_profile]["model"]
    messages = [{"role": "user", "content": transcription}]
    chat_completion = client.chat.completions.create(
        messages = messages,
        model = selected_model,
    )
    print(selected_model)

    return chat_completion.choices[0].message.content
    
@cl.on_chat_start
async def start():
    await cl.Message(
        content="Welcome to the Weya-Takehome bot. Press `P` to talk!"
    ).send()


@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    if chunk.isStart:
        buffer = BytesIO()
        # This is required for whisper to recognize the file type
        buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
        # Initialize the session for a new audio stream
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime_type", chunk.mimeType)
    cl.user_session.get("audio_buffer").write(chunk.data)


@cl.on_audio_end
async def on_audio_end(elements: list[ElementBased]):
# Get the audio buffer from the session
    audio_buffer: BytesIO = cl.user_session.get("audio_buffer")
    audio_buffer.seek(0)  # Move the file pointer to the beginning
    audio_file = audio_buffer.read()
    audio_mime_type: str = cl.user_session.get("audio_mime_type")
    with open(r"weya_takehome\chainlit_app\input_audio.mp3", "wb") as f:
        f.write(audio_file)
    # Create the audio element to send in the message
    input_audio_el = cl.Audio(
        mime=audio_mime_type, content=audio_file, name="audio.mp3"
    )
    await cl.Message(
        author="You", 
        type="user_message",
        content="",
        elements=[input_audio_el, *elements]
    ).send()

    transcription = await speech_to_text(r"weya_takehome\chainlit_app\input_audio.mp3")
    print(transcription)
    text_answer = await generate_text_answer(transcription)
    print(text_answer)

    output_name, output_audio = await text_to_speech(text_answer, audio_mime_type)
    
    output_audio_el = cl.Audio(
        name=output_name,
        auto_play=True,
        mime=audio_mime_type,
        content=output_audio,
    )
    answer_message = await cl.Message(content="").send()

    answer_message.elements = [output_audio_el]

    try:
        os.remove(r"weya_takehome\chainlit_app\input_audio.mp3")
    except:
        pass
    await answer_message.update()

# Define profiles. Setting up only 2 profiles as of now.
profiles = {
    "Gemma-7b-it": {
        "name": "Gemma-7b-it",
        "description": "The underlying LLM model is **Gemma-7b-it**. It's a lightweight model from Google.",
        "icon": "https://www.rappler.com/tachyon/2024/02/gemma-google.jpg",
        "model": "gemma-7b-it",
        "starters": [
            cl.Starter(
                label="What is LLM?",
                message="What is LLM. Explain in brief along with examples",
            ),
            cl.Starter(
                label="Advantages of Gemma-7b-it?",
                message="What are the advantages of Gemma-7b-it model over other models? Be descriptive and clear.",
            )
        ]
    },
    "Llama3-8b-8192": {
        "name": "Llama3-8b-8192",
        "description": "The underlying LLM model is **Llama3-8b-8192**. It's Meta's model trained on 8B parameters",
        "icon": "https://cdn.prod.website-files.com/65b8f370a600366bc7cf9b20/660e66b997dc8488ed5ac43a_meta.png",
        "model": "Llama3-8b-8192",
        "starters": [
            cl.Starter(
                label="What is LLM?",
                message="What is LLM. Explain in brief along with examples",
            ),
            cl.Starter(
                label="Advantages of Llama3-8b-8192?",
                message="What are the advantages of Llama3-8b-8192 model over other models? Be descriptive and clear.",
            )
        ]
    }
}


# Set chat profiles
@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    return [
        cl.ChatProfile(
            name=profiles["Gemma-7b-it"]["name"],
            markdown_description=profiles["Gemma-7b-it"]["description"],
            icon=profiles["Gemma-7b-it"]["icon"],
            starters=profiles["Gemma-7b-it"]["starters"]
        ),
        cl.ChatProfile(
            name=profiles["Llama3-8b-8192"]["name"],
            markdown_description=profiles["Llama3-8b-8192"]["description"],
            icon=profiles["Llama3-8b-8192"]["icon"],
            starters=profiles["Llama3-8b-8192"]["starters"]
        )
    ]

# On message function to dynamically select the model
@cl.on_message
async def main(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    selected_model = profiles[chat_profile]["model"]

    message_body = f'''
                    Generate the answer for the following message and use these factors:
                    Accuracy and Relevance: The answer should be accurate and relevant to user queries, using a knowledge base or external data sources as needed.
                    User Experience: clear and concise responses that are easy to understand.
                    The message is: 
                    {message.content}
                   '''
    print(selected_model)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message_body,
            }
        ],
        model=selected_model,
    )
    await cl.Message(
        content=f"{chat_completion.choices[0].message.content}",
    ).send()
