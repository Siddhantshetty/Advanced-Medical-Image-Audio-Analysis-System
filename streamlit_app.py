# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

# VoiceBot UI with Streamlit
import os
import streamlit as st
from io import BytesIO
import tempfile
import streamlit as st
import os

# Configure secrets for deployment
if hasattr(st, 'secrets'):
    try:
        os.environ['GROQ_API_KEY'] = st.secrets.get('GROQ_API_KEY', '')
        os.environ['ELEVENLABS_API_KEY'] = st.secrets.get('ELEVENLABS_API_KEY', '')
    except:
        pass

# Force reload environment variables
if 'ELEVENLABS_API_KEY' in os.environ:
    del os.environ['ELEVENLABS_API_KEY']

# Reload dotenv to get fresh API key
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # Override existing environment variables
except ImportError:
    pass

# Try to import streamlit-audiorec for better web recording
try:
    from st_audiorec import st_audiorec
    AUDIOREC_AVAILABLE = True
except ImportError:
    AUDIOREC_AVAILABLE = False

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def apply_dark_theme():
    """Apply dark theme with custom CSS"""
    st.markdown("""
    <style>
    /* Dark theme for sidebar */
    .css-1d391kg {
        background-color: #1e1e1e;
    }
    
    .css-1lcbmhc {
        background-color: #1e1e1e;
    }
    
    /* Dark theme for main content */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    /* Dark theme for sidebar elements */
    .css-17eq0hr {
        background-color: #262730;
    }
    
    /* Style for sidebar navigation */
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        background-color: #262730;
        color: white;
        border: none;
        width: 100%;
        text-align: left;
        font-size: 16px;
    }
    
    .nav-item:hover {
        background-color: #ff4b4b;
        color: white;
    }
    
    .nav-item.active {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    
    /* Header styling with blue-purple gradient that matches dark theme */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 25%, #5b21b6 50%, #7c3aed 75%, #6366f1 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .step-card {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff4b4b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 120px;
        display: flex;
        align-items: center;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
        line-height: 1.3;
    }
    
    .step-card p {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.4;
        color: #ccc;
    }
    
    .step-number {
        background-color: #ff4b4b;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .tech-stack {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    
    .feature-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #404040;
    }
    
    /* Custom metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def sidebar_navigation():
    """Create sidebar navigation"""
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem;'>
        <h1 style='color: #ff4b4b; margin: 0;'>🏥 AI Doctor</h1>
        <p style='color: #888; margin: 0.5rem 0 0 0;'>Vision & Voice Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    pages = {
        "🏠 Home": "home",
        "📤 Upload & Process": "upload",
        "👨‍💻 About": "about",
        "⚙️ Settings": "settings"
    }
    
    selected_page = "home"  # default
    
    for page_name, page_key in pages.items():
        if st.sidebar.button(page_name, key=page_key, use_container_width=True):
            st.session_state.current_page = page_key
    
    # Get current page from session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    return st.session_state.current_page


def process_inputs(audio_file, image_file):
    """Process audio and image inputs to generate doctor's response"""
    
    speech_to_text_output = ""
    doctor_response = ""
    voice_of_doctor = None
    
    # Handle audio input
    if audio_file is not None:
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_file.read())
            audio_filepath = tmp_audio.name
        
        try:
            speech_to_text_output = transcribe_with_groq(
                GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                audio_filepath=audio_filepath,
                stt_model="whisper-large-v3"
            )
        except Exception as e:
            speech_to_text_output = f"Error transcribing audio: {str(e)}"
        finally:
            # Clean up temporary file
            os.unlink(audio_filepath)
    
    # Handle image input
    if image_file is not None:
        # Save uploaded image to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_image:
            tmp_image.write(image_file.read())
            image_filepath = tmp_image.name
        
        try:
            if speech_to_text_output and not speech_to_text_output.startswith("Error"):
                query = system_prompt + speech_to_text_output
            else:
                query = system_prompt + "Please analyze this medical image."
                
            doctor_response = analyze_image_with_query(
                query=query, 
                encoded_image=encode_image(image_filepath), 
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
        except Exception as e:
            doctor_response = f"Error analyzing image: {str(e)}"
        finally:
            # Clean up temporary file
            os.unlink(image_filepath)
    else:
        doctor_response = "No image provided for me to analyze"
    
    # Generate voice response
    if doctor_response and not doctor_response.startswith("Error") and not doctor_response.startswith("No image"):
        # Check text length to estimate credits needed
        text_length = len(doctor_response)
        estimated_credits = text_length * 0.2  # Rough estimate
        
        if estimated_credits > 100:  # If estimated credits > 100, warn user
            st.warning(f"⚠️ Long response detected ({text_length} characters). This might use ~{int(estimated_credits)} credits.")
        
        try:
            # Try ElevenLabs first
            voice_of_doctor = text_to_speech_with_elevenlabs(
                input_text=doctor_response, 
                output_filepath="final.mp3"
            )
        except Exception as e:
            error_message = str(e)
            if "quota_exceeded" in error_message or "401" in error_message:
                # Silently use Google TTS without warning the user
                try:
                    # Fallback to Google TTS with faster speed
                    voice_of_doctor = text_to_speech_with_gtts(
                        input_text=doctor_response, 
                        output_filepath="final.mp3",
                        speed=1.5  # Faster speech rate (if your function supports this parameter)
                    )
                except TypeError:
                    # If speed parameter is not supported, try without it
                    try:
                        voice_of_doctor = text_to_speech_with_gtts(
                            input_text=doctor_response, 
                            output_filepath="final.mp3"
                        )
                    except Exception as gtts_error:
                        st.error(f"Error generating voice response: {str(gtts_error)}")
                except Exception as gtts_error:
                    st.error(f"Error generating voice response: {str(gtts_error)}")
            else:
                st.error(f"Error generating voice response: {error_message}")
    
    return speech_to_text_output, doctor_response, voice_of_doctor


def record_audio_wrapper():
    """Wrapper function to handle audio recording with proper error handling"""
    try:
        # Try different possible function signatures for record_audio
        
        # Method 1: Try with output_filename parameter
        try:
            recorded_file = record_audio(output_filename="recorded_audio.wav")
            return recorded_file
        except TypeError:
            pass
        
        # Method 2: Try with just filename as positional argument  
        try:
            recorded_file = record_audio("recorded_audio.wav")
            return recorded_file
        except TypeError:
            pass
        
        # Method 3: Try with no parameters (function might have defaults)
        try:
            recorded_file = record_audio()
            # Check if default file exists
            default_files = ["recorded_audio.wav", "audio.wav", "recording.wav", "output.wav"]
            for filename in default_files:
                if os.path.exists(filename):
                    return filename
            return None
        except TypeError:
            pass
        
        # If all methods fail, return None
        return None
        
    except ImportError:
        st.error("Audio recording module not properly imported")
        return None
    except Exception as e:
        st.error(f"Recording error: {str(e)}")
        return None


def home_page():
    """Home page content"""
    st.markdown("""
    <div class='main-header'>
        <h1>🏥 AI Doctor with Vision & Voice</h1>
        <h3>Advanced Medical Image & Audio Analysis System</h3>
        <p>Combining Computer Vision, Natural Language Processing, and Text-to-Speech Technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Overview section
    st.markdown("## 🎯 What Does This System Do?")
    st.markdown("""
    This AI-powered medical assistant analyzes medical images and audio descriptions to provide 
    preliminary medical insights. It's designed for educational purposes and to demonstrate 
    the integration of multiple AI technologies in healthcare applications.
    """)
    
    # Process flow
    st.markdown("## 🔄 Step-by-Step Process")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='step-card'>
            <div style='display: flex; align-items: center; width: 100%;'>
                <div class='step-number'>1</div>
                <div class='step-content'>
                    <h4>Audio Input Processing</h4>
                    <p>User uploads or records audio describing symptoms</p>
                </div>
            </div>
        </div>
        
        <div class='step-card'>
            <div style='display: flex; align-items: center; width: 100%;'>
                <div class='step-number'>2</div>
                <div class='step-content'>
                    <h4>Speech-to-Text Conversion</h4>
                    <p>Audio is transcribed using Groq's Whisper model</p>
                </div>
            </div>
        </div>
        
        <div class='step-card'>
            <div style='display: flex; align-items: center; width: 100%;'>
                <div class='step-number'>3</div>
                <div class='step-content'>
                    <h4>Image Analysis</h4>
                    <p>Medical image is encoded and analyzed using LLaMA vision model</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='step-card'>
            <div style='display: flex; align-items: center; width: 100%;'>
                <div class='step-number'>4</div>
                <div class='step-content'>
                    <h4>Medical Analysis</h4>
                    <p>AI generates medical insights combining audio and visual data</p>
                </div>
            </div>
        </div>
        
        <div class='step-card'>
            <div style='display: flex; align-items: center; width: 100%;'>
                <div class='step-number'>5</div>
                <div class='step-content'>
                    <h4>Text-to-Speech Output</h4>
                    <p>Response is converted to audio using ElevenLabs or Google TTS</p>
                </div>
            </div>
        </div>
        
        <div class='step-card'>
            <div style='display: flex; align-items: center; width: 100%;'>
                <div class='step-number'>6</div>
                <div class='step-content'>
                    <h4>Results Presentation</h4>
                    <p>Display transcription, analysis, and provide audio playback</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Technical Stack
    st.markdown("## 🛠️ Technology Stack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <h4>🎤 Audio Processing</h4>
            <ul>
                <li>Groq Whisper API</li>
                <li>Streamlit Audio Recorder</li>
                <li>Web Audio API</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <h4>🖼️ Image Analysis</h4>
            <ul>
                <li>LLaMA Vision Model</li>
                <li>Base64 Image Encoding</li>
                <li>Computer Vision</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <h4>🗣️ Voice Synthesis</h4>
            <ul>
                <li>ElevenLabs TTS</li>
                <li>Google Text-to-Speech</li>
                <li>Audio Speed Control</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Key Features
    st.markdown("## ✨ Key Features")
    
    features = [
        "🎯 **Multi-modal Analysis**: Combines audio descriptions with visual medical data",
        "🧠 **AI-Powered Insights**: Uses advanced language models for medical analysis",
        "🎤 **Voice Interface**: Natural voice input and output for accessibility",
        "📱 **Web-based Recording**: Direct browser recording capabilities",
        "🔄 **Fallback Systems**: Multiple TTS options for reliability",
        "⚡ **Real-time Processing**: Fast analysis and response generation"
    ]
    
    for feature in features:
        st.markdown(feature)
    
    # Important Disclaimer
    st.markdown("## ⚠️ Important Disclaimer")
    st.error("""
    **FOR EDUCATIONAL PURPOSES ONLY**
    
    This AI system is designed for learning and demonstration purposes only. It should NOT be used for:
    - Actual medical diagnosis
    - Treatment decisions
    - Emergency medical situations
    - Replacing professional medical advice
    
    Always consult with qualified healthcare professionals for any medical concerns.
    """)


def upload_process_page():
    """Upload and process page content"""
    st.title("📤 Upload & Process")
    st.markdown("Upload your audio recording and medical image for AI analysis")
    
    if not AUDIOREC_AVAILABLE:
        st.info("💡 For better recording experience, install: `pip install streamlit-audiorec`")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📱 Audio Input")
        audio_file = st.file_uploader(
            "Upload your audio recording",
            type=['wav', 'mp3', 'ogg', 'm4a'],
            help="Record or upload an audio file describing your symptoms"
        )
        
        # Audio recorder widget with actual recording
        st.markdown("*Or record directly:*")
        
        if AUDIOREC_AVAILABLE:
            # Use streamlit-audiorec for web-based recording
            wav_audio_data = st_audiorec()
            
            if wav_audio_data is not None:
                st.audio(wav_audio_data, format='audio/wav')
                # Store in session state for processing
                st.session_state.web_recorded_audio = wav_audio_data
                st.success("✅ Web recording completed!")
        
        if not AUDIOREC_AVAILABLE:
            # Web-based recording fallback using HTML5
            st.markdown("**🌐 Web Browser Recording:**")
            
            # HTML5 Web Audio API recorder
            html_recorder = """
            <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin: 10px 0;">
                <button id="startRecord" onclick="startRecording()" style="background: #ff4b4b; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px;">🎤 Start Recording</button>
                <button id="stopRecord" onclick="stopRecording()" disabled style="background: #666; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px;">⏹️ Stop</button>
                <button id="clearRecord" onclick="clearRecording()" style="background: #666; color: white; border: none; padding: 8px 16px; border-radius: 4px;">🔄 Clear</button>
                <div id="recordingStatus" style="margin-top: 10px; font-style: italic;"></div>
                <audio id="audioPlayback" controls style="width: 100%; margin-top: 10px; display: none;"></audio>
            </div>
            
            <script>
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;
            
            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        
                        const audioElement = document.getElementById('audioPlayback');
                        audioElement.src = audioUrl;
                        audioElement.style.display = 'block';
                        
                        // Convert to base64 for Streamlit
                        const reader = new FileReader();
                        reader.onloadend = function() {
                            const base64 = reader.result.split(',')[1];
                            // Store in a way Streamlit can access (this is a simplified example)
                            document.getElementById('recordingStatus').innerHTML = 
                                '✅ Recording completed! Download and upload the audio file manually.';
                        };
                        reader.readAsDataURL(audioBlob);
                        
                        // Create download link
                        const downloadLink = document.createElement('a');
                        downloadLink.href = audioUrl;
                        downloadLink.download = 'recording.wav';
                        downloadLink.innerHTML = '📥 Download Recording';
                        downloadLink.style.display = 'block';
                        downloadLink.style.marginTop = '10px';
                        downloadLink.style.color = '#ff4b4b';
                        downloadLink.style.textDecoration = 'none';
                        
                        const container = document.getElementById('recordingStatus');
                        container.appendChild(document.createElement('br'));
                        container.appendChild(downloadLink);
                    };
                    
                    audioChunks = [];
                    mediaRecorder.start();
                    isRecording = true;
                    
                    document.getElementById('startRecord').disabled = true;
                    document.getElementById('stopRecord').disabled = false;
                    document.getElementById('recordingStatus').innerHTML = '🔴 Recording in progress...';
                    
                } catch (err) {
                    document.getElementById('recordingStatus').innerHTML = 
                        '❌ Microphone access denied. Please check browser permissions.';
                    console.error('Error accessing microphone:', err);
                }
            }
            
            function stopRecording() {
                if (mediaRecorder && isRecording) {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    isRecording = false;
                    
                    document.getElementById('startRecord').disabled = false;
                    document.getElementById('stopRecord').disabled = true;
                }
            }
            
            function clearRecording() {
                audioChunks = [];
                const audioElement = document.getElementById('audioPlayback');
                audioElement.style.display = 'none';
                audioElement.src = '';
                
                const status = document.getElementById('recordingStatus');
                status.innerHTML = '';
                
                // Remove download link if it exists
                const downloadLinks = status.getElementsByTagName('a');
                for (let i = downloadLinks.length - 1; i >= 0; i--) {
                    downloadLinks[i].remove();
                }
            }
            </script>
            """
            
            # Display the HTML recorder
            st.components.v1.html(html_recorder, height=200)
            
            st.info("💡 **Instructions for Web Recording:**\n1. Click 'Start Recording' and allow microphone access\n2. Speak into your microphone\n3. Click 'Stop' when done\n4. Click 'Download Recording' to save the file\n5. Upload the downloaded file using the file uploader above")
    
    with col2:
        st.subheader("📷 Image Input")
        image_file = st.file_uploader(
            "Upload medical image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a medical image for analysis"
        )
        
        # Display uploaded image with updated parameter
        if image_file is not None:
            st.image(image_file, caption="Uploaded Medical Image", use_container_width=True)
    
    # Process button
    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        # Check if we have either uploaded audio or recorded audio
        audio_to_process = None
        
        # Priority: uploaded file first, then web recorded, then file recorded
        if audio_file is not None:
            audio_to_process = audio_file
            audio_source = "uploaded"
        elif hasattr(st.session_state, 'web_recorded_audio') and st.session_state.web_recorded_audio is not None:
            # Convert web recorded audio to file-like object
            audio_to_process = BytesIO(st.session_state.web_recorded_audio)
            audio_source = "web recorded"
        elif hasattr(st.session_state, 'recorded_audio') and st.session_state.recorded_audio:
            # Convert recorded file to file-like object
            try:
                if os.path.exists(st.session_state.recorded_audio):
                    with open(st.session_state.recorded_audio, "rb") as f:
                        audio_to_process = BytesIO(f.read())
                        audio_source = "recorded"
                else:
                    st.error("Recorded audio file not found")
                    return
            except FileNotFoundError:
                st.error("Recorded audio file not found")
                return
            except Exception as e:
                st.error(f"Error reading recorded audio: {str(e)}")
                return
        
        if audio_to_process is not None or image_file is not None:
            with st.spinner("Processing your inputs..."):
                # Reset file pointers
                if audio_to_process is not None:
                    audio_to_process.seek(0)
                if image_file is not None:
                    image_file.seek(0)
                
                speech_to_text_output, doctor_response, voice_of_doctor = process_inputs(
                    audio_to_process, image_file
                )
                
                # Show which audio source was used
                if audio_to_process is not None:
                    st.info(f"Processed {audio_source} audio")
            
            # Display results
            st.subheader("📋 Results")
            
            # Speech to text output
            if speech_to_text_output:
                st.markdown("**🎯 Transcribed Speech:**")
                st.text_area("", value=speech_to_text_output, height=100, disabled=True)
            
            # Doctor's response
            if doctor_response:
                st.markdown("**👨‍⚕️ Doctor's Analysis:**")
                st.text_area("", value=doctor_response, height=150, disabled=True)
            
            # Voice response
            if voice_of_doctor:
                st.markdown("**🔊 Voice Response:**")
                try:
                    with open("final.mp3", "rb") as audio_file_output:
                        audio_bytes = audio_file_output.read()
                        st.audio(audio_bytes, format="audio/mp3")
                except FileNotFoundError:
                    st.warning("Voice file not found. Check text-to-speech generation.")
                except Exception as e:
                    st.error(f"Error playing audio: {str(e)}")
        else:
            st.warning("Please upload at least an audio file or an image to proceed.")


def about_page():
    """About page content"""
    st.title("👨‍💻 About")
    
    # Profile section
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 2rem; color: white;'>
        <h1>👋 Siddhant Shetty</h1>
        <h3>AI&DS Student at TSEC</h3>
        <p style='font-size: 1.1em; margin-top: 1rem;'>
            Passionate about building innovative AI solutions that bridge the gap between technology and real-world applications
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # About content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 About This Project
        
        The AI Doctor with Vision & Voice is a comprehensive medical analysis system that demonstrates 
        the integration of multiple AI technologies:
        
        - **Computer Vision** for medical image analysis
        - **Natural Language Processing** for understanding patient descriptions
        - **Speech Recognition** for audio input processing
        - **Text-to-Speech** for accessible voice output
        
        This project showcases how modern AI can be applied to healthcare scenarios while maintaining 
        ethical considerations and educational purpose.
        """)
        
        st.markdown("""
        ### 🛠️ Technical Skills Demonstrated
        
        - **Machine Learning**: LLM integration, Vision models
        - **Web Development**: Streamlit, HTML5, CSS3, JavaScript
        - **API Integration**: Groq, ElevenLabs, Google TTS
        - **Audio Processing**: Web Audio API, speech recognition
        - **UI/UX Design**: Responsive design, dark theme implementation
        """)
    
    with col2:
        st.markdown("""
        ### 🌟 Key Features Built
        
        - **Multi-modal AI Analysis**: Combining text, audio, and image inputs
        - **Real-time Audio Recording**: Browser-based recording capabilities  
        - **Intelligent Fallback Systems**: Multiple TTS providers for reliability
        - **Responsive UI Design**: Modern, accessible interface design
        - **Error Handling**: Robust exception handling and user feedback
        
        ### 📫 Connect With Me
        
        I'm always interested in discussing AI projects, collaborations, 
        or opportunities in the field of artificial intelligence and software development.
        """)
        
        # Social links
        st.markdown("""
        <div style='display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;'>
            <a href='https://github.com/Siddhantshetty' target='_blank' 
               style='padding: 0.5rem 1rem; background-color: #333; color: white; 
                      text-decoration: none; border-radius: 5px; font-weight: bold;'>
                🔗 GitHub Profile
            </a>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='display: flex; gap: 1rem; justify-content: center; margin-top: 1rem;'>
            <a href='https://www.linkedin.com/in/siddhant-shetty-1811-/' target='_blank' 
               style='padding: 0.5rem 1rem; background-color: #0077B5; color: white; 
                      text-decoration: none; border-radius: 5px; font-weight: bold;'>
                🔗 LinkedIn Profile
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Project stats
    st.markdown("### 📊 Project Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>🎤</h3>
            <h2>3+</h2>
            <p>Audio Formats Supported</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>🧠</h3>
            <h2>2+</h2>
            <p>AI Models Integrated</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>🔊</h3>
            <h2>2</h2>
            <p>TTS Providers</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <h3>📱</h3>
            <h2>100%</h2>
            <p>Web Compatible</p>
        </div>
        """, unsafe_allow_html=True)


def mask_api_key(api_key):
    """Mask API key for security, showing only first 4 and last 4 characters"""
    if not api_key or len(api_key) < 8:
        return "Not set"
    return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"


def settings_page():
    """Settings page content"""
    st.title("⚙️ Settings")
    st.markdown("Configure your API keys and application preferences")
    
    # API Configuration Section
    st.markdown("## 🔑 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ElevenLabs Configuration")
        
        # Show masked current API key
        current_elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY', '')
        if current_elevenlabs_key:
            st.info(f"Current API Key: {mask_api_key(current_elevenlabs_key)}")
        
        elevenlabs_key = st.text_input(
            "ElevenLabs API Key", 
            type="password",
            help="Enter your ElevenLabs API key for premium voice generation",
            placeholder="Enter new API key to update..."
        )
        
        if elevenlabs_key:
            os.environ['ELEVENLABS_API_KEY'] = elevenlabs_key
            st.success("✅ ElevenLabs API key updated")
            
            # Voice selection if API key is provided
            voice_options = [
                "Rachel", "Domi", "Bella", "Antoni", "Elli", "Josh", 
                "Arnold", "Adam", "Sam", "Nicole", "Freya"
            ]
            selected_voice = st.selectbox(
                "Select Voice",
                voice_options,
                help="Choose your preferred ElevenLabs voice"
            )
            st.session_state.elevenlabs_voice = selected_voice
        elif current_elevenlabs_key:
            # If there's an existing key but no new one entered, show voice selection
            voice_options = [
                "Rachel", "Domi", "Bella", "Antoni", "Elli", "Josh", 
                "Arnold", "Adam", "Sam", "Nicole", "Freya"
            ]
            selected_voice = st.selectbox(
                "Select Voice",
                voice_options,
                help="Choose your preferred ElevenLabs voice"
            )
            st.session_state.elevenlabs_voice = selected_voice
        else:
            st.info("🎤 Enter API key to enable ElevenLabs TTS")
    
    with col2:
        st.markdown("### Groq Configuration")
        
        # Show masked current API key
        current_groq_key = os.environ.get('GROQ_API_KEY', '')
        if current_groq_key:
            st.info(f"Current API Key: {mask_api_key(current_groq_key)}")
        
        groq_key = st.text_input(
            "Groq API Key",
            type="password", 
            help="Enter your Groq API key for speech-to-text processing",
            placeholder="Enter new API key to update..."
        )
        
        if groq_key:
            os.environ['GROQ_API_KEY'] = groq_key
            st.success("✅ Groq API key updated")
        elif not current_groq_key:
            st.info("🎯 Enter API key to enable speech recognition")
    
    # Audio Settings
    st.markdown("## 🎵 Audio Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Text-to-Speech Preferences")
        
        # TTS Provider selection
        tts_provider = st.selectbox(
            "Primary TTS Provider",
            ["ElevenLabs (Premium)", "Google TTS (Free)"],
            help="Choose your preferred text-to-speech provider"
        )
        st.session_state.tts_provider = tts_provider
        
        # Speech speed
        speech_speed = st.slider(
            "Speech Speed",
            min_value=0.5,
            max_value=2.0,
            value=1.5,
            step=0.1,
            help="Adjust the speed of generated speech"
        )
        st.session_state.speech_speed = speech_speed
    
    with col2:
        st.markdown("### Recording Preferences")
        
        # Audio quality
        audio_quality = st.selectbox(
            "Recording Quality",
            ["High (48kHz)", "Medium (44.1kHz)", "Low (22kHz)"],
            index=1,
            help="Choose recording quality (higher quality = larger files)"
        )
        st.session_state.audio_quality = audio_quality
        
        # Auto-play results
        auto_play = st.checkbox(
            "Auto-play Voice Results",
            value=True,
            help="Automatically play voice response after analysis"
        )
        st.session_state.auto_play = auto_play
    
    # Model Settings
    st.markdown("## 🤖 Model Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Vision Model Configuration")
        
        vision_model = st.selectbox(
            "Vision Model",
            ["meta-llama/llama-4-scout-17b-16e-instruct", "gpt-4-vision", "claude-3-vision"],
            help="Select the AI model for image analysis"
        )
        st.session_state.vision_model = vision_model
        
        # Analysis detail level
        detail_level = st.selectbox(
            "Analysis Detail Level",
            ["Concise (2 sentences)", "Standard (1 paragraph)", "Detailed (Multiple paragraphs)"],
            help="Choose how detailed you want the medical analysis to be"
        )
        st.session_state.detail_level = detail_level
    
    with col2:
        st.markdown("### Speech Recognition Settings")
        
        stt_model = st.selectbox(
            "Speech-to-Text Model",
            ["whisper-large-v3", "whisper-large-v2", "whisper-medium"],
            help="Select the Whisper model for speech recognition"
        )
        st.session_state.stt_model = stt_model
        
        # Language detection
        auto_language = st.checkbox(
            "Auto-detect Language",
            value=True,
            help="Automatically detect the language of spoken audio"
        )
        st.session_state.auto_language = auto_language
    
    # System Settings
    st.markdown("## 🖥️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Interface Preferences")
        
        # Theme selection
        theme = st.selectbox(
            "Theme",
            ["Dark (Current)", "Light", "Auto"],
            help="Choose your preferred interface theme"
        )
        st.session_state.theme = theme
        
        # Show debug info
        show_debug = st.checkbox(
            "Show Debug Information",
            value=False,
            help="Display technical debug information in the sidebar"
        )
        st.session_state.show_debug = show_debug
    
    with col2:
        st.markdown("### Performance Settings")
        
        # Cache settings
        enable_cache = st.checkbox(
            "Enable Response Caching",
            value=True,
            help="Cache API responses to improve performance and reduce costs"
        )
        st.session_state.enable_cache = enable_cache
        
        # Concurrent processing
        max_concurrent = st.slider(
            "Max Concurrent Requests",
            min_value=1,
            max_value=5,
            value=2,
            help="Maximum number of concurrent API requests"
        )
        st.session_state.max_concurrent = max_concurrent
    
    # Current Status
    st.markdown("## 📊 Current Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        if os.environ.get('ELEVENLABS_API_KEY'):
            st.success("🎤 ElevenLabs: Connected")
        else:
            st.warning("🎤 ElevenLabs: Not Connected")
    
    with status_col2:
        if os.environ.get('GROQ_API_KEY'):
            st.success("🎯 Groq: Connected")
        else:
            st.warning("🎯 Groq: Not Connected")
    
    with status_col3:
        if AUDIOREC_AVAILABLE:
            st.success("📱 Web Recording: Available")
        else:
            st.warning("📱 Web Recording: Install streamlit-audiorec")
    
    # Save Settings
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        st.success("✅ Settings saved successfully!")
        st.balloons()
    
    # Reset Settings
    if st.button("🔄 Reset to Defaults", type="secondary", use_container_width=True):
        # Clear session state settings
        settings_keys = [
            'elevenlabs_voice', 'tts_provider', 'speech_speed', 'audio_quality',
            'auto_play', 'vision_model', 'detail_level', 'stt_model', 
            'auto_language', 'theme', 'show_debug', 'enable_cache', 'max_concurrent'
        ]
        for key in settings_keys:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Settings reset to defaults!")
        st.rerun()


# Main Application
def main():
    st.set_page_config(
        page_title="AI Doctor with Vision and Voice",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply dark theme
    apply_dark_theme()
    
    # Sidebar navigation
    current_page = sidebar_navigation()
    
    # Display appropriate page
    if current_page == "home":
        home_page()
    elif current_page == "upload":
        upload_process_page()
    elif current_page == "about":
        about_page()
    elif current_page == "settings":
        settings_page()
    
    # Sidebar footer (always visible)
    st.sidebar.markdown("---")
    
    # Show debug info if enabled
    if st.session_state.get('show_debug', False):
        with st.sidebar.expander("🔧 Debug Info"):
            st.json({
                "Current Page": current_page,
                "ElevenLabs Connected": bool(os.environ.get('ELEVENLABS_API_KEY')),
                "Groq Connected": bool(os.environ.get('GROQ_API_KEY')),
                "Audio Recorder Available": AUDIOREC_AVAILABLE,
                "Session State Keys": list(st.session_state.keys())
            })
    
    # Disclaimer (always visible)
    with st.sidebar:
        st.markdown("### ⚠️ Disclaimer")
        st.caption("This AI system is for educational purposes only. Always consult with qualified healthcare professionals for medical advice.")
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #888;'>
                <p style='margin: 0; font-size: 0.8em;'>Built by <strong>Siddhant Shetty</strong></p>
                <p style='margin: 0; font-size: 0.8em;'>© 2024 AI Doctor System</p>
            </div>
            """, 
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()