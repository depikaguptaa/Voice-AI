# Voice AI Project

## Dependencies
- **Language:** Python 3.12
- **IDE used:** VS Code
- **STT:** OpenAI's Whisper (https://github.com/openai/whisper)
- **TTS:** ElevenLabs API (https://github.com/elevenlabs/elevenlabs-python)
- **Interface:** Chainlit
- **Dependency Management Tool:** Poetry
- **Extra dependencies:** ffmpeg (https://www.gyan.dev/ffmpeg/builds/)
    *[**about ffmpeg:**]  We are using ffmpeg for Whisper to locate audio file, else it'll pop an error saying that "No such file/directory found". Hence, it is recommended to install the ffmpeg from the given link and set up it in the environment PATH. A detailed approach can be found here: https://phoenixnap.com/kb/ffmpeg-windows*
- **LLM:** Groq (Llama3-8b-8192, Gemma-7b-it)


## Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

- Python (make sure it's installed and added to your PATH)
- Poetry (for dependency management and packaging in Python)

### Installation

1. **Install Poetry** (if not installed)

    ```bash
    pip install poetry
    ```

2. **Clone the Repository**

    Open the Weya-Takehome repository in any IDE (VSCode is preferred for working with notebooks).

3. **Install Dependencies**

    Navigate to the project directory and run:

    ```bash
    poetry install
    ```

    This will install all the dependencies listed in the `pyproject.toml` file.

4. **Set Up Poetry Environment**

    Run:

    ```bash
    poetry shell
    ```

    This will activate the poetry environment and give an environment path. 

5. **Select Interpreter in IDE**

    In VSCode, go to `Select Interpreter` and navigate to the given environment path:
    - Go to the environment path -> `scripts` -> select `python.exe`

### Running the Project

1. **Run the Chainlit App**

    ```bash
    poetry run chainlit run .\weya_takehome\chainlit_app\app.py -w
    ```

    This will start the project.

### Whisper by OpenAI

Whisper is a general-purpose speech recognition model. It is trained on a large dataset of diverse audio and is also a multitasking model that can perform multilingual speech recognition, speech translation, and language identification.

We've used several models like tiny, base and small to test our input and as per our observation:
- Tiny model works good for English files
- Base model works good for English and satisfactory for Hindi files
- Small models works good for both English and Hindi files.

But just to respect the UX and time taken to convert the audio into the text, we've gone for **base** model as it gives satisfying response.

Further, we can use API's for the same, but STT for different languages is not well optimized either and this is a good-to-go approach to start with on-local machine model to save cost.
