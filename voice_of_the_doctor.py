# voice_of_the_doctor.py - Fixed version based on your original code

import os
from gtts import gTTS
import elevenlabs
from elevenlabs.client import ElevenLabs
import subprocess
import platform

# Fixed API key variable name to match Streamlit app
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVEN_API_KEY")

def text_to_speech_with_gtts_old(input_text, output_filepath):
    """Original gTTS function without auto-play"""
    language = "en"
    audioobj = gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)

def text_to_speech_with_elevenlabs_old(input_text, output_filepath):
    """Original ElevenLabs function without auto-play"""
    if not ELEVENLABS_API_KEY:
        raise Exception("ElevenLabs API key not found")
    
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.generate(
        text=input_text,
        voice="Aria",
        output_format="mp3_22050_32",
        model="eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)

def text_to_speech_with_gtts(input_text, output_filepath, auto_play=False):
    """
    gTTS function with optional auto-play and proper return value
    
    Args:
        input_text (str): Text to convert to speech
        output_filepath (str): Path to save the audio file
        auto_play (bool): Whether to auto-play the audio (default: False for Streamlit)
    
    Returns:
        str: Path to the generated audio file if successful, None otherwise
    """
    try:
        language = "en"
        audioobj = gTTS(
            text=input_text,
            lang=language,
            slow=False
        )
        audioobj.save(output_filepath)
        
        # Check if file was created successfully
        if not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
            raise Exception("Audio file was not created or is empty")
        
        # Auto-play only if requested (disabled by default for Streamlit)
        if auto_play:
            try:
                os_name = platform.system()
                if os_name == "Darwin":  # macOS
                    subprocess.run(['afplay', output_filepath])
                elif os_name == "Windows":  # Windows
                    subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
                elif os_name == "Linux":  # Linux
                    subprocess.run(['aplay', output_filepath])
                else:
                    print("Unsupported operating system for auto-play")
            except Exception as e:
                print(f"Auto-play failed: {e}")
        
        return output_filepath
        
    except Exception as e:
        raise Exception(f"Google TTS failed: {str(e)}")

def text_to_speech_with_elevenlabs(input_text, output_filepath, auto_play=False):
    """
    ElevenLabs TTS function with optional auto-play and proper return value
    
    Args:
        input_text (str): Text to convert to speech
        output_filepath (str): Path to save the audio file
        auto_play (bool): Whether to auto-play the audio (default: False for Streamlit)
    
    Returns:
        str: Path to the generated audio file if successful, None otherwise
    """
    try:
        if not ELEVENLABS_API_KEY:
            raise Exception("ElevenLabs API key not found. Set ELEVENLABS_API_KEY or ELEVEN_API_KEY environment variable.")
        
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Generate audio
        audio = client.generate(
            text=input_text,
            voice="Aria",
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        
        # Save audio
        elevenlabs.save(audio, output_filepath)
        
        # Check if file was created successfully
        if not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
            raise Exception("Audio file was not created or is empty")
        
        # Auto-play only if requested (disabled by default for Streamlit)
        if auto_play:
            try:
                os_name = platform.system()
                if os_name == "Darwin":  # macOS
                    subprocess.run(['afplay', output_filepath])
                elif os_name == "Windows":  # Windows
                    subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
                elif os_name == "Linux":  # Linux
                    subprocess.run(['aplay', output_filepath])
                else:
                    print("Unsupported operating system for auto-play")
            except Exception as e:
                print(f"Auto-play failed: {e}")
        
        return output_filepath
        
    except Exception as e:
        raise Exception(f"ElevenLabs TTS failed: {str(e)}")

# Enhanced TTS function with fallback
def enhanced_text_to_speech(input_text, output_filepath="final.mp3", preferred_tts="elevenlabs"):
    """
    Enhanced TTS with fallback from ElevenLabs to Google TTS
    
    Args:
        input_text (str): Text to convert to speech
        output_filepath (str): Path to save the audio file
        preferred_tts (str): Preferred TTS service ('elevenlabs' or 'gtts')
    
    Returns:
        tuple: (success: bool, audio_file_path: str, message: str)
    """
    
    if not input_text or not input_text.strip():
        return False, None, "No text provided"
    
    # Try preferred TTS first
    if preferred_tts == "elevenlabs" and ELEVENLABS_API_KEY:
        try:
            result = text_to_speech_with_elevenlabs(input_text, output_filepath, auto_play=False)
            if result:
                return True, result, "ElevenLabs TTS successful"
        except Exception as e:
            print(f"ElevenLabs failed: {e}")
            # Continue to fallback
    
    # Fallback to Google TTS
    try:
        result = text_to_speech_with_gtts(input_text, output_filepath, auto_play=False)
        if result:
            return True, result, "Google TTS successful"
    except Exception as e:
        print(f"Google TTS failed: {e}")
        return False, None, f"All TTS methods failed. Last error: {str(e)}"

# Test functions
def test_gtts():
    """Test Google TTS"""
    input_text = "Hi this is AI with Hassan, testing Google TTS!"
    try:
        result = text_to_speech_with_gtts(input_text, "test_gtts.mp3")
        print(f"Google TTS test: {'✅ Success' if result else '❌ Failed'}")
        return result
    except Exception as e:
        print(f"Google TTS test failed: {e}")
        return None

def test_elevenlabs():
    """Test ElevenLabs TTS"""
    input_text = "Hi this is AI with Hassan, testing ElevenLabs TTS!"
    try:
        result = text_to_speech_with_elevenlabs(input_text, "test_elevenlabs.mp3")
        print(f"ElevenLabs TTS test: {'✅ Success' if result else '❌ Failed'}")
        return result
    except Exception as e:
        print(f"ElevenLabs TTS test failed: {e}")
        return None

def test_enhanced_tts():
    """Test enhanced TTS with fallback"""
    input_text = "Hi this is Siddhant, testing enhanced TTS with fallback!"
    try:
        success, filepath, message = enhanced_text_to_speech(input_text, "test_enhanced.mp3")
        print(f"Enhanced TTS test: {'✅' if success else '❌'} {message}")
        return success
    except Exception as e:
        print(f"Enhanced TTS test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing TTS functions...")
    print(f"ElevenLabs API Key present: {'✅' if ELEVENLABS_API_KEY else '❌'}")
    print("-" * 50)
    
    # Test Google TTS
    test_gtts()
    
    # Test ElevenLabs TTS
    test_elevenlabs()
    
    # Test Enhanced TTS
    test_enhanced_tts()
    
    print("-" * 50)
    print("Testing complete!")
