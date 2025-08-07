# Advanced Medical Image Audio Analysis System
**Medical Chatbot with Multimodal LLM (Vision and Voice)**

The Advanced Medical Image Audio Analysis System is an innovative healthcare solution that combines cutting-edge vision and voice capabilities to provide intelligent medical analysis. The system can analyze medical images, engage in voice conversations, and provide comprehensive medical insights using state-of-the-art AI models.

## Features

- 🧠 **Multimodal AI Brain**: Powered by Llama 3 Vision for analyzing medical images and text
- 🎤 **Voice Input**: Real-time audio recording and speech-to-text transcription using OpenAI Whisper
- 🔊 **Voice Output**: Text-to-speech conversion using gTTS and ElevenLabs
- 🖼️ **Image Analysis**: Medical image processing and analysis capabilities
- 🌐 **Interactive UI**: User-friendly Streamlit web interface
- ⚡ **Fast Inference**: Groq API for rapid AI model inference

## Technical Architecture

The project is built with a modular architecture consisting of four main phases:

1. **Brain of the Doctor**: Multimodal LLM setup with vision capabilities
2. **Voice of the Patient**: Audio recording and speech-to-text processing
3. **Voice of the Doctor**: Text-to-speech synthesis for AI responses
4. **Streamlit UI**: Web-based interface for seamless interaction

## Tools and Technologies

- **AI Inference**: Groq API
- **Vision Model**: Llama 3 Vision (Meta's open-source multimodal model)
- **Speech-to-Text**: OpenAI Whisper (best open-source transcription model)
- **Text-to-Speech**: gTTS & ElevenLabs
- **UI Framework**: Streamlit
- **Programming Language**: Python
- **Development Environment**: VS Code

## Prerequisites

Before setting up the project, ensure you have the following:

- Python 3.8 or higher
- FFmpeg and PortAudio installed on your system
- Groq API key
- ElevenLabs API key (optional, for premium TTS)

## Installation Guide

### 1. Installing FFmpeg and PortAudio

#### macOS
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg and PortAudio
brew install ffmpeg portaudio
```

#### Linux (Debian-based distributions)
```bash
# Update package list
sudo apt update

# Install FFmpeg and PortAudio
sudo apt install ffmpeg portaudio19-dev
```

#### Windows
1. **Download FFmpeg:**
   - Visit [FFmpeg Downloads](https://ffmpeg.org/download.html)
   - Download the latest static build for Windows
   - Extract to `C:\ffmpeg`

2. **Add FFmpeg to PATH:**
   - Search for "Environment Variables" in Start menu
   - Edit system environment variables
   - Add `C:\ffmpeg\bin` to PATH variable

3. **Install PortAudio:**
   - Download from [PortAudio Downloads](http://www.portaudio.com/download.html)
   - Follow installation instructions

### 2. Setting Up Python Virtual Environment

Choose one of the following methods:

#### Using pip and venv (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Using Pipenv
```bash
# Install Pipenv
pip install pipenv

# Install dependencies and create virtual environment
pipenv install

# Activate virtual environment
pipenv shell
```

#### Using Conda
```bash
# Create conda environment
conda create --name medical-analysis python=3.11

# Activate environment
conda activate medical-analysis

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

## Usage

Run the application phases in the following order:

### Phase 1: Setup the Brain of the Doctor
```bash
python brain_of_the_doctor.py
```
This phase initializes the multimodal LLM with vision capabilities using the Groq API.

### Phase 2: Setup Voice of the Patient
```bash
python voice_of_the_patient.py
```
This phase configures audio recording and speech-to-text transcription using OpenAI Whisper.

### Phase 3: Setup Voice of the Doctor
```bash
python voice_of_the_doctor.py
```
This phase sets up text-to-speech conversion for AI responses.

### Phase 4: Launch Streamlit UI
```bash
python streamlit_app.py
```
or
```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

## Project Structure

```
advanced-medical-image-audio-analysis/
├── brain_of_the_doctor.py      # Multimodal LLM setup
├── voice_of_the_patient.py     # Speech-to-text processing
├── voice_of_the_doctor.py      # Text-to-speech synthesis
├── streamlit_app.py            # Streamlit web interface
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # Project documentation
```

## API Keys Setup

### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Create an account and navigate to API Keys
3. Generate a new API key
4. Add it to your `.env` file

### ElevenLabs API Key (Optional)
1. Visit [ElevenLabs](https://elevenlabs.io/)
2. Create an account and go to your profile
3. Generate an API key
4. Add it to your `.env` file

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Ensure FFmpeg is properly installed and added to your system PATH
2. **PortAudio errors**: Install the development version of PortAudio for your system
3. **API key errors**: Verify your API keys are correctly set in the `.env` file
4. **Module not found**: Ensure you've activated your virtual environment and installed all dependencies

### System-Specific Notes

- **macOS**: You may need to grant microphone permissions to your terminal/IDE
- **Windows**: Ensure you're running the command prompt as administrator when installing system dependencies
- **Linux**: Some distributions may require additional audio system packages

## Future Improvements

- 🎯 **Enhanced Models**: Integration with state-of-the-art paid LLMs for improved vision capabilities
- 🏥 **Medical Specialization**: Fine-tuning vision models specifically on medical imaging datasets
- 🌍 **Multilingual Support**: Adding support for multiple languages in voice and text processing
- 📊 **Analytics Dashboard**: Patient interaction analytics and medical insights tracking
- 🔒 **Security Enhancements**: HIPAA-compliant data handling and privacy features

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Meta for the open-source Llama 3 Vision model
- OpenAI for the Whisper speech-to-text model
- Groq for providing fast AI inference capabilities
- The open-source community for the various tools and libraries used

## Contact

For questions, issues, or contributions, please open an issue on the GitHub repository.

---

**Note**: This is an educational/research project. Please consult with qualified medical professionals for actual medical advice and diagnosis.

---

## About the Advanced Medical Image Audio Analysis System

This system represents the future of healthcare technology, combining advanced AI capabilities to create a comprehensive medical analysis platform that can process both visual medical data and audio interactions simultaneously.
