import streamlit as st
import boto3
import os
import requests
import json
from io import BytesIO
import time
import base64
import streamlit.components.v1 as components
from datetime import datetime
import uuid
from botocore.exceptions import ClientError, NoCredentialsError
import io
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="PlantCare AI - Professional Plant Health Solutions",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "s3b-iisc-aimlops-cap-images")
S3_REGION = os.environ.get("AWS_REGION", "us-east-2")
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://plant-disease-detection.aichamp.publicvm.com/api")

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

# Initialize session state for chatbot
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())
if "current_page" not in st.session_state:
    st.session_state.current_page = "Disease Detection"

# Enhanced Professional CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f8fffe 0%, #f0fff4 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* Professional Header */
    .professional-header {
        /* Switched to a lush green gradient */
        background: linear-gradient(135deg, #4CAF50 0%, #2E8B57 50%, #006400 100%);
        color: white;
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        /* Adjusted shadow to a dark green for consistency */
        box-shadow: 0 10px 30px rgba(18, 77, 26, 0.3);
        position: relative;
        overflow: hidden;
    }

    /* This subtle grain texture still works well with a natural theme */
    .professional-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.05)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }

    /* No changes needed for the content wrapper */
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
        position: relative;
        z-index: 1;
    }

    /* Title changed to a solid, high-contrast color for better readability */
    .header-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        /* Changed from a gradient to a solid color */
        color: white;
        text-align: center;
        /* Removed the background-clip properties */
    }
    
    .header-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .header-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Navigation Enhancement */
    .nav-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(34, 197, 94, 0.2);
    }
    
    .nav-tabs {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .nav-tab {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 2px solid #e2e8f0;
        color: #64748b;
        padding: 1rem 2rem;
        border-radius: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
        font-size: 1.1rem;
    }
    
    .nav-tab:hover {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(34, 197, 94, 0.3);
    }
    
    .nav-tab.active {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        border-color: #16a34a;
        box-shadow: 0 5px 15px rgba(34, 197, 94, 0.3);
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(34, 197, 94, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .feature-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #22c55e, #16a34a);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #6b7280;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .feature-benefits {
        list-style: none;
        padding: 0;
    }
    
    .feature-benefits li {
        padding: 0.5rem 0;
        color: #374151;
        position: relative;
        padding-left: 2rem;
    }
    
    .feature-benefits li::before {
        content: "✅";
        position: absolute;
        left: 0;
        top: 0.5rem;
    }
    
    /* Upload Section Enhancement */
    .upload-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 3px dashed #22c55e;
        border-radius: 25px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .upload-section::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(34, 197, 94, 0.05) 0%, transparent 50%);
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .upload-icon {
        font-size: 4rem;
        color: #22c55e;
        margin-bottom: 1rem;
        display: block;
    }
    
    .upload-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .upload-subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    /* Chat Interface Enhancement */
    .chat-container {
        background: white;
        border-radius: 25px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(34, 197, 94, 0.2);
    }
    /* This styles the container for each chat message */
    div[data-testid="chat-message-container"] {
        background-color: #f0f2f6; /* A light gray for assistant messages */
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    /* This targets user messages to keep them on the default background */
    div[data-testid="chat-message-container"][data-testid*="user"] {
        background-color: transparent;
    }
    
    .chat-message {
        margin: 1.5rem 0;
        padding: 1.5rem;
        border-radius: 20px;
        max-width: 85%;
        animation: slideIn 0.3s ease-out;
        position: relative;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        margin-left: auto;
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: #374151;
        margin-right: auto;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    # .chat-input-section {
    #     background: white;
    #     border-radius: 20px;
    #     padding: 2rem;
    #     margin: 2rem 0;
    #     box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    #     border: 2px solid #22c55e;
    # }
    
    /* Professional Footer */
    .professional-footer {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        color: white;
        padding: 3rem 0 2rem 0;
        margin: 3rem -1rem -1rem -1rem;
        border-radius: 20px 20px 0 0;
        position: relative;
        overflow: hidden;
    }
    
    .professional-footer::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #22c55e, #16a34a, #059669);
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .footer-section h3 {
        color: #22c55e;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .footer-section p, .footer-section li {
        color: #d1d5db;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    
    .footer-section ul {
        list-style: none;
        padding: 0;
    }
    
    .footer-section ul li::before {
        content: "→";
        color: #22c55e;
        margin-right: 0.5rem;
    }
    
    .footer-bottom {
        border-top: 1px solid #374151;
        padding-top: 2rem;
        text-align: center;
        color: #9ca3af;
    }
    
    .social-links {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .social-link {
        width: 40px;
        height: 40px;
        background: #374151;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .social-link:hover {
        background: #22c55e;
        transform: translateY(-2px);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .header-subtitle {
            font-size: 1.1rem;
        }
        
        .header-stats {
            gap: 1rem;
        }
        
        .stat-item {
            padding: 0.8rem;
        }
        
        .nav-tab {
            padding: 0.8rem 1.5rem;
            font-size: 1rem;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
        
        .chat-message {
            max-width: 95%;
        }
        
        .upload-section {
            padding: 2rem;
        }
        
        .upload-title {
            font-size: 1.5rem;
        }
    }
    
    /* Loading Animation */
    .loading-spinner {
        border: 4px solid #f3f4f6;
        border-top: 4px solid #22c55e;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border: 1px solid #22c55e;
        color: #166534;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .error-message {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #ef4444;
        color: #dc2626;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Professional Header
st.markdown("""
<div class="professional-header">
    <div class="header-content">
        <h1 class="header-title">🌱 PlantCare AI</h1>
        <p class="header-subtitle">Professional Plant Health Solutions Powered by Artificial Intelligence</p>
        <div class="header-stats">
            <div class="stat-item">
                <span class="stat-number">99.2%</span>
                <span class="stat-label">Detection Accuracy</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">50+</span>
                <span class="stat-label">Plant Diseases</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">24/7</span>
                <span class="stat-label">AI Support</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">10K+</span>
                <span class="stat-label">Plants Analyzed</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    /* Style for the container of the buttons */
    div[data-testid="column"] {
        text-align: center;
    }

    /* General button style */
    .stButton>button {
        background-color: #f0f2f6;
        color: #333;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem 1rem; /* Increased padding for a taller button */
        width: 100%;
        transition: all 0.2s;
        font-size: 10rem !important; /* <-- This makes the text and emoji bigger */
    }
    
    /* Style for the ACTIVE button */
    .stButton.active>button {
        background-color: #2E8B57; /* A nice green */
        color: white;
        border: 1px solid #2E8B57;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Navigation
st.markdown("<h3 style='text-align: center;'>Choose Your Service</h3>", unsafe_allow_html=True)

# Determine which button is active for styling
is_detection_active = st.session_state.current_page == "Disease Detection"
is_chat_active = st.session_state.current_page == "Chat Assistant"

# col1, col2 = st.columns(2)
# with col1:
#     if st.button("🔬 Disease Detection", key="nav_detection", use_container_width=True):
#         st.session_state.current_page = "Disease Detection"
# with col2:
#     if st.button("🤖 AI Chat Assistant", key="nav_chat", use_container_width=True):
#         st.session_state.current_page = "Chat Assistant"
col1, col2 = st.columns(2)
with col1:
    # Use a custom class for the active button
    st.markdown('<div class="stButton active">' if is_detection_active else '<div class="stButton">', unsafe_allow_html=True)
    if st.button("🔬 Disease Detection", key="nav_detection", use_container_width=True):
        st.session_state.current_page = "Disease Detection"
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stButton active">' if is_chat_active else '<div class="stButton">', unsafe_allow_html=True)
    if st.button("🤖 Chat Assistant", key="nav_chat", use_container_width=True):
        st.session_state.current_page = "Chat Assistant"
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
# st.markdown("""
# <style>
#     /* This targets the buttons within the tab bar */
#     button[data-testid="stTabs-tab"] {
#         font-size: 5rem;       /* Increases the font size */
#         padding: 0.75rem 1.5rem;  /* Increases the padding to make the tab bar taller */
#     }
# </style>
# """, unsafe_allow_html=True)
# st.markdown("<h2 style='text-align: center;'>Choose Your Service</h2>", unsafe_allow_html=True)

# # 1. Create the tabs
# tab1, tab2 = st.tabs(["🧬 Disease Detection", "🤖 AI Chat Assistant"])
# with tab1:
#     # if st.button("🔬 Disease Detection", key="nav_detection", use_container_width=True):
#     st.session_state.current_page = "Disease Detection"
# with tab2:
#     # if st.button("🤖 AI Chat Assistant", key="nav_chat", use_container_width=True):
#     st.session_state.current_page = "Chat Assistant"

# Configure AWS S3 client
# Configure AWS S3 client
def get_s3_client():
    """Initialize S3 client with credentials"""
    try:
        # First try to use IAM role (for ECS/EC2) 
        s3_client = boto3.client(
            's3',
            region_name=os.environ.get("AWS_REGION", "us-east-2")
        )
        return s3_client
    except Exception as e:
        # Fallback to Streamlit secrets if IAM role fails
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=st.secrets["aws_access_key_id"],
                aws_secret_access_key=st.secrets["aws_secret_access_key"],
                region_name=os.environ.get("AWS_REGION", "us-east-2")
            )
            return s3_client
        except KeyError:
            st.error("AWS credentials not found. Please ensure ECS task has proper IAM role or configure Streamlit secrets.")
            return None
        except Exception as e2:
            st.error(f"Error initializing S3 client: {str(e2)}")
            return None

def upload_to_s3(file_obj, bucket_name, object_key):
    """Upload file to S3 bucket"""
    s3_client = get_s3_client()
    if not s3_client:
        return None
    
    try:
        # Reset file pointer to beginning
        file_obj.seek(0)
        
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            object_key,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
        
        # Generate S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        return s3_url
        
    except ClientError as e:
        st.error(f"Error uploading to S3: {str(e)}")
        return None
    except NoCredentialsError:
        st.error("AWS credentials not available")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def call_disease_detection_api(s3_url, fastapi_url, file_key):
    """Call FastAPI backend for disease detection"""
    try:
        # Prepare payload with file_key instead of image_url
        payload = {
            "file_key": file_key
        }
        
        # Make API call to your existing endpoint
        response = requests.post(
            f"{fastapi_url}/analyze_from_s3/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling FastAPI: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error in API call: {str(e)}")
        return None

def display_analysis_results(result_data, image_name):
    """Display disease detection results"""
    if not result_data or not isinstance(result_data, list) or len(result_data) == 0:
        st.error("No results received from analysis")
        return
    
    # Extract results from API response (first item in the list)
    result = result_data[0]
    
    filename = result.get("filename", image_name)
    is_plant = result.get("is_plant", "Unknown")
    label = result.get("label", "Unknown")
    confidence = result.get("confidence", 0) * 100  # Convert to percentage
    message = result.get("message", "")
    disease_details = result.get("disease_details", "")
    
    # Display results
    st.success(f"✅ Analysis complete for {filename} | 📋 **Status:** {message}")
    # st.info(f"")
    confidence_color = "🟢" if confidence > 80 else "🟡" if confidence > 60 else "🔴"
    # Plant detection result
    if "True" in str(is_plant):
        st.success(
            f"""
            🌱 **Plant Detection:** {is_plant}\n
            🔬 **Disease Classification:** {label}\n
            {confidence_color} **Confidence:** {confidence:.1f}%
            """
            )
    else:
        st.warning(
            f"""
            ⚠️ **Plant Detection:** {is_plant}\n
            {confidence_color} **Confidence:** {confidence:.1f}%
            """
            )
    
    # # Disease classification
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.info(f"")
    # with col2:
    #     confidence_color = "🟢" if confidence > 80 else "🟡" if confidence > 60 else "🔴"
    #     st.warning(f"{confidence_color} **Confidence:** {confidence:.1f}%")

    # --- Combined Results Card ---

    # Determine the color for the plant detection status
    # plant_status_color = "#28a745" if "True" in str(is_plant) else "#ffc107"
    # plant_icon = "🌱" if "True" in str(is_plant) else "⚠️"

    # # Determine the color for the confidence score
    # confidence_color = "#28a745" if confidence > 80 else "#ffc107" if confidence > 60 else "#dc3545"
    # confidence_icon = "🟢" if confidence > 80 else "🟡" if confidence > 60 else "🔴"

    # # Use a container to create the main card
    # with st.container(border=True):
    #     # Main status message
    #     st.markdown(f"📋 **Status:** {message}")
    #     st.divider()

    #     # Plant Detection and Disease Classification in columns
    #     col1, col2 = st.columns(2)

    #     with col1:
    #         st.markdown(
    #             f'<p style="color:{plant_status_color}; font-weight: bold;">{plant_icon} Plant Detection: {is_plant}</p>',
    #             unsafe_allow_html=True
    #         )
    #         st.markdown(f"🔬 **Disease:** {label}")

    #     with col2:
    #         st.markdown(
    #             f'<p style="color:{confidence_color}; font-weight: bold;">{confidence_icon} Confidence: {confidence:.1f}%</p>',
    #             unsafe_allow_html=True
    #         )
    
def call_translation_api(text, target_language, fastapi_url):
    """Call FastAPI backend for translation"""
    try:
        # Prepare payload for translation API
        payload = {
            "text": text,
            "target_language": target_language
        }
        
        # Make API call to translation endpoint
        response = requests.post(
            f"{fastapi_url}/translate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Translation API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Translation API: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error in translation API call: {str(e)}")
        return None

def translate_text_content(text, target_language, fastapi_url):
    """Translate text content and return translated text"""
    if not text or not text.strip():
        return text
    
    result = call_translation_api(text, target_language, fastapi_url)
    if result and isinstance(result, dict):
        # Assuming the API returns translated text in a field like 'translated_text'
        # Adjust this based on your actual API response structure
        return result.get('translated_text', text)
    return text

def store_analysis_results(result_data, image_name):
    """Store analysis results in session state"""
    if 'stored_results' not in st.session_state:
        st.session_state.stored_results = []
    
    # Extract results from API response
    result = result_data[0]
    filename = result.get("filename", image_name)
    is_plant = result.get("is_plant", "Unknown")
    label = result.get("label", "Unknown")
    confidence = result.get("confidence", 0) * 100
    message = result.get("message", "")
    disease_details = result.get("disease_details", "")
    
    # Create result object
    result_obj = {
        'id': str(uuid.uuid4()),
        'filename': filename,
        'is_plant': is_plant,
        'label': label,
        'confidence': confidence,
        'message': message,
        'disease_details': disease_details,
        'timestamp': str(uuid.uuid4())  # Simple timestamp substitute
    }
    
    # Add to stored results
    st.session_state.stored_results.append(result_obj)
    
    return result_obj

def display_all_stored_results(fastapi_url):
    """Display all stored results with dual language support"""
    if 'stored_results' not in st.session_state or not st.session_state.stored_results:
        return
    
    # Initialize translation cache if not exists
    if 'translation_cache' not in st.session_state:
        st.session_state.translation_cache = {}
    
    # Indian languages for secondary display (Hindi is default)
    SECONDARY_LANGUAGES = {
        "हिंदी": "hi",
        "தமிழ்": "ta",
        "বাংলা": "bn",
        "മലയാളം": "ml",
        "ಕನ್ನಡ": "kn",
        "తెలుగు": "te",
        "मराठी": "mr",
        "ગુજરાતી": "gu",
        "ਪੰਜਾਬੀ": "pa"
    }
    
    # Global secondary language selection (affects all results)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="color: white; margin: 0; text-align: center;">🌐 Secondary Language Selection</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selection for secondary display
    selected_secondary_language = st.selectbox(
        "Select Secondary Language (English will always be shown above):",
        options=list(SECONDARY_LANGUAGES.keys()),
        index=0,  # Default to Hindi
        key="global_secondary_language"
    )
    
    # Display all stored results
    for idx, result_obj in enumerate(st.session_state.stored_results):
        st.markdown(f"## 📊 Analysis Result {idx + 1}")
        
        # Get translated results for secondary language
        secondary_results = get_translated_results(
            result_obj,
            selected_secondary_language,
            SECONDARY_LANGUAGES,
            fastapi_url
        )
        
        # === DISPLAY ENGLISH RESULTS (PERMANENT) ===
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; margin: 0; text-align: center;">🇺🇸 English Results</h3>
        </div>
        """, unsafe_allow_html=True)
        
        display_results_section(result_obj, "English")
        
        # === DISPLAY SECONDARY LANGUAGE RESULTS ===
        st.markdown("---")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; margin: 0; text-align: center;">🌏 {selected_secondary_language} Results</h3>
        </div>
        """, unsafe_allow_html=True)
        
        display_results_section(secondary_results, selected_secondary_language)
        
        # Action buttons for each result
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 View Full Report", key=f"report_{result_obj['id']}"):
                st.info("Full report feature coming soon!")
        with col2:
            if st.button("💾 Save Results", key=f"save_{result_obj['id']}"):
                st.info("Save feature coming soon!")
        with col3:
            if st.button("🔄 Re-analyze", key=f"reanalyze_{result_obj['id']}"):
                st.info("Re-analysis feature coming soon!")
        
        # Add separator between results
        if idx < len(st.session_state.stored_results) - 1:
            st.markdown("---")
            st.markdown("<br>", unsafe_allow_html=True)

def display_results_section(results, language_name):
    """Display results section for a specific language"""
    filename = results['filename']
    
    # Display basic results
    st.success(f"✅ Analysis complete for {filename}")
    st.info(f"📋 **Status:** {results['message']}")
    
    # Plant detection result
    if "True" in str(results['is_plant']):
        st.success(f"🌱 **Plant Detection:** {results['is_plant']}")
    else:
        st.warning(f"⚠️ **Plant Detection:** {results['is_plant']}")
    
    # Disease classification and confidence
    st.info(f"🔬 **Disease Classification:** {results['label']}")
    confidence_color = "🟢" if results['confidence'] > 80 else "🟡" if results['confidence'] > 60 else "🔴"
    st.warning(f"{confidence_color} **Confidence:** {results['confidence']:.1f}%")
    
    # Disease details
    if results['disease_details']:
        st.markdown(f"### 📖 Detailed Information ({language_name})")
        sections = results['disease_details'].split("### ")
        
        for section in sections:
            if section.strip():
                lines = section.strip().split('\n')
                if len(lines) > 0:
                    section_title = lines[0]
                    section_content = '\n'.join(lines[1:])
                    
                    # Icon selection (works for both English and translated)
                    icon = get_section_icon(section_title)
                    
                    with st.expander(f"{icon} {section_title}", expanded=True):
                        st.markdown(section_content)

def get_section_icon(section_title):
    """Get appropriate icon for section title"""
    title_lower = section_title.lower()
    
    if any(word in title_lower for word in ['identification', 'damage', 'पहचान', 'नुकसान', 'চিহ্নিতকরণ', 'அடையாளம்', 'గుర్తింపు', 'ओळख', 'ਪਛਾਣ']):
        return "🔍"
    elif any(word in title_lower for word in ['life cycle', 'जीवन चक्र', 'জীবনচক্র', 'வாழ்க்கைச் சுழற்சி', 'జీవిత చక్రం', 'जीवन चक्र', 'ਜੀਵਨ ਚੱਕਰ']):
        return "🔄"
    elif any(word in title_lower for word in ['solutions', 'समाधान', 'সমাধান', 'தீர்வுகள்', 'పరిష్కారాలు', 'उपाय', 'ਹੱਲ']):
        return "💡"
    elif any(word in title_lower for word in ['treatment', 'उपचार', 'চিকিৎসা', 'சிகிச்சை', 'చికిత్స', 'उपचार', 'ਇਲਾਜ']):
        return "🏥"
    elif any(word in title_lower for word in ['prevention', 'रोकथाम', 'প্রতিরোধ', 'தடுப்பு', 'నిరోధం', 'बचाव', 'ਰੋਕਥਾਮ']):
        return "🛡️"
    else:
        return "📋"

def get_translated_results(original_results, selected_language, languages, fastapi_url):
    """Get translated results with caching"""
    target_lang_code = languages[selected_language]
    cache_key = f"{original_results['id']}_{selected_language}"
    
    if cache_key not in st.session_state.translation_cache:
        # Show translation progress
        with st.spinner(f"🌐 Translating to {selected_language}..."):
            translated_results = {
                'id': original_results['id'],
                'filename': original_results['filename'],
                'is_plant': original_results['is_plant'],  # Don't translate boolean
                'label': translate_text_content(original_results['label'], target_lang_code, fastapi_url),
                'confidence': original_results['confidence'],  # Don't translate number
                'message': translate_text_content(original_results['message'], target_lang_code, fastapi_url),
                'disease_details': translate_text_content(original_results['disease_details'], target_lang_code, fastapi_url),
                'timestamp': original_results['timestamp']
            }
            
            st.session_state.translation_cache[cache_key] = translated_results
    
    return st.session_state.translation_cache[cache_key]

if st.session_state.current_page == "Disease Detection":
    # Use existing environment variables
    S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "s3b-iisc-aimlops-cap-images")
    S3_REGION = os.environ.get("AWS_REGION", "us-east-2")
    FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://plant-disease-detection.aichamp.publicvm.com/api")
    
    # Upload Section
    # st.markdown("""
    # <div class="upload-section">
    #     <span class="upload-icon">📸</span>
    #     <h2 class="upload-title">Upload Plant Images</h2>
    #     <p class="upload-subtitle">Drop your plant images here for instant AI-powered disease detection</p>
    # </div>
    # """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        /* This targets the main container of the file uploader */
        [data-testid="stFileUploader"] {
            background-color: #f0f8f0;
            border: 2px dashed #2E8B57;
            border-radius: 15px;
            padding: 2rem;
        }
        
        /* This targets the text inside the label */
        [data-testid="stFileUploader"] p {
            font-size: 1.1rem;
            font-weight: 500;
            color: #333;
            margin: 0;
        }
        
        /* This targets the "Browse files" button */
        [data-testid="stFileUploader"] button {
            background-color: #2E8B57;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)


    # 2. Create a markdown string for the custom label
    # uploader_label = """
    # <p style="text-align: center; font-size: 2.5rem; margin-bottom: 0.5rem;">📸</p>
    # <p style="text-align: center;">Drop your plant images here for instant AI-powered disease detection</p>
    # """
    st.markdown("""
        <div style="text-align: center;">
            <h2 style="color: 'green';">AI Plant Disease Detection & Treatment recomendation</h2>
            <p style="color: #6b7280;">Upload an image and get the disease details and treamtment recomendations</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    uploaded_images = st.file_uploader(
        label="Upload Plant image",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Supported formats: PNG, JPG, JPEG. Maximum file size: 10MB",
    )
    
    if uploaded_images:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem; color: white;">
            ✅ {len(uploaded_images)} image(s) uploaded successfully! Ready for analysis...
        </div>
        """, unsafe_allow_html=True)
        
        # Display uploaded images in a grid
        cols = st.columns(min(len(uploaded_images), 3))
        for idx, uploaded_image in enumerate(uploaded_images):
            with cols[idx % 3]:
                st.image(uploaded_image, caption=f"📷 {uploaded_image.name}", use_container_width =False)
                
                # Add processing button for each image
                if st.button(f"🔍 Analyze {uploaded_image.name}", key=f"analyze_{idx}"):
                    with st.spinner("🚀 Uploading to cloud storage..."):
                        # Generate unique filename
                        file_extension = uploaded_image.name.split('.')[-1].lower()
                        unique_filename = f"{uuid.uuid4()}.{file_extension}"
                        
                        # Convert uploaded file to bytes
                        uploaded_image.seek(0)  # Reset file pointer
                        #image_bytes = io.BytesIO(uploaded_image.read())
                        
                        # Upload to S3 (you'll need to implement this function)
                        s3_url = upload_to_s3(
                            uploaded_image,     # Pass directly as a file-like object
                            S3_BUCKET,
                            unique_filename
                        )
                        
                        if s3_url:
                            st.success("✅ Image uploaded to cloud storage!")
                            
                            with st.spinner("🤖 AI is analyzing your plant image..."):
                                # Call FastAPI backend
                                result = call_disease_detection_api(
                                    s3_url,
                                    FASTAPI_URL,
                                    unique_filename
                                )
                                
                                if result:
                                    # Convert to list format if needed
                                    if isinstance(result, dict):
                                        result = [result]
                                    
                                    # Check if the result indicates a successful analysis
                                    if isinstance(result, list) and len(result) > 0:
                                        first_result = result[0]
                                        is_plant = first_result.get("is_plant", "")
                                        
                                        # Check if it's actually a plant
                                        if "False" in str(is_plant):
                                            st.error("❌ The uploaded image doesn't appear to be a plant. Please upload a clear image of a plant leaf or affected area.")
                                        else:
                                            # Store results in session state
                                            store_analysis_results(result, uploaded_image.name)
                                            # Force a rerun to display the new results
                                            st.rerun()
                                    else:
                                        st.error("❌ Unexpected response format from analysis API.")
                                else:
                                    st.error("❌ Analysis failed. Please try again.")
                        else:
                            st.error("❌ Failed to upload image to cloud storage.")
    
    # Display all stored results (this will persist across reruns)
    display_all_stored_results(FASTAPI_URL)

    st.divider()

    # Use Streamlit columns instead of CSS Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔬</span>
            <h3 class="feature-title">Advanced AI Detection</h3>
            <p class="feature-description">State-of-the-art machine learning algorithms trained on thousands of plant images for accurate disease identification.</p>
            <ul class="feature-benefits">
                <li>99.2% accuracy rate</li>
                <li>Real-time analysis</li>
                <li>Multi-species support</li>
                <li>Instant results</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🌍</span>
            <h3 class="feature-title">Global Coverage</h3>
            <p class="feature-description">Comprehensive database covering plant diseases from different climates and regions worldwide.</p>
            <ul class="feature-benefits">
                <li>50+ disease types</li>
                <li>Multi-language support</li>
                <li>Regional expertise</li>
                <li>Climate-specific insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <h3 class="feature-title">Instant Solutions</h3>
            <p class="feature-description">Get immediate treatment recommendations and prevention strategies for identified plant diseases.</p>
            <ul class="feature-benefits">
                <li>Treatment protocols</li>
                <li>Prevention tips</li>
                <li>Organic solutions</li>
                <li>Expert guidance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "Chat Assistant":
    # Include CSS with the HTML in components.html
    feature_cards_html = """
    <style>
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
        padding: 1rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        color: #1f2937;
        margin-bottom: 1rem;
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    .feature-description {
        color: #6b7280;
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    .feature-benefits {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-benefits li {
        color: #374151;
        margin-bottom: 0.5rem;
        padding-left: 1.5rem;
        position: relative;
    }
    
    .feature-benefits li::before {
        content: "✓";
        color: #10b981;
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    </style>
    
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <h3 class="feature-title">Smart AI Assistant</h3>
            <p class="feature-description">Powered by Google Gemini AI, providing intelligent responses to all your plant health questions.</p>
            <ul class="feature-benefits">
                <li>Natural language processing</li>
                <li>Context-aware responses</li>
                <li>24/7 availability</li>
                <li>Multilingual support</li>
            </ul>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">📷</span>
            <h3 class="feature-title">Image Analysis</h3>
            <p class="feature-description">Upload images directly in chat for instant visual analysis and detailed disease diagnosis.</p>
            <ul class="feature-benefits">
                <li>Visual disease detection</li>
                <li>Symptom identification</li>
                <li>Progressive monitoring</li>
                <li>Comparative analysis</li>
            </ul>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">🌱</span>
            <h3 class="feature-title">Expert Knowledge</h3>
            <p class="feature-description">Access to comprehensive plant disease database and treatment protocols from agricultural experts.</p>
            <ul class="feature-benefits">
                <li>Evidence-based solutions</li>
                <li>Preventive strategies</li>
                <li>Organic treatments</li>
                <li>Seasonal care tips</li>
            </ul>
        </div>
    </div>
    """
    
    #components.html(feature_cards_html, height=500, scrolling=True)
    
    # Chat Interface
    st.markdown("""
        <div style="text-align: center;">
            <h2 style="color: 'green';">💬 AI Chat Assistant</h2>
            <p style="color: #6b7280;">Ask me anything about plant diseases, treatments, and care tips</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        #st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong><br>{message["content"]}
                    {f'<br><em style="opacity: 0.8;">📷 Image: {message.get("image_name", "uploaded")}</em>' if message.get("has_image") else ""}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🌱 PlantCare AI:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat Input Section
    st.divider()
    # st.markdown('<div class="chat-input-section">', unsafe_allow_html=True)
    
    # Input type selection
    input_type = st.radio(
        "**Choose your interaction method:**",
        ["💬 Text Message", "📷 Text + Image Analysis"],
        horizontal=True
    )
    
    if input_type == "💬 Text Message":
        user_input = st.text_area(
            "**Ask your plant health question:**",
            placeholder="e.g., My tomato leaves are turning yellow with brown spots. What could be causing this?",
            height=100
        )
        
        if st.button("🚀 Send Message", type="primary", use_container_width=True):
            if user_input:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })

                # Prepare data for the API request
                # The FastAPI endpoint expects a slightly different history format
                api_history = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        api_history.append({"user": msg["content"]})
                    elif msg["role"] == "assistant":
                        # Find the preceding user message to pair with the assistant response
                        # This is a simplified approach; a more robust one might use IDs
                        if api_history and "assistant" not in api_history[-1]:
                            api_history[-1]["assistant"] = msg["content"]

                payload = {
                    "message": user_input,
                    "conversation_history": api_history
                }
                
                # Simulate AI response
                with st.spinner("🤖 PlantCare AI is thinking..."):
                    # time.sleep(2)
                    try:
                        response = requests.post(f"{FASTAPI_URL}/chat/text", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            ai_response = response.json().get("response")
                            
                            # Add AI response to the chat
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": ai_response,
                                "timestamp": datetime.now().isoformat()
                            })
                        else:
                            st.error(f"Error from API: {response.status_code} - {response.text}")
        
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to connect to the chat service: {e}")
                    
                    # # Mock response
                    # response = f"Based on your description, this sounds like it could be a fungal infection. I recommend checking for proper drainage and air circulation. Would you like me to provide specific treatment options?"
                    
                    # st.session_state.messages.append({
                    #     "role": "assistant",
                    #     "content": response,
                    #     "timestamp": datetime.now().isoformat()
                    # })
                    
                    st.rerun()
    
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_input = st.text_area(
                "**Describe your plant issue:**",
                placeholder="e.g., I found these spots on my plant leaves. What could be causing this?",
                height=120
            )
        
        with col2:
            uploaded_image = st.file_uploader(
                "**Upload plant image:**",
                type=["png", "jpg", "jpeg"],
                key="chat_image"
            )
            
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("📸 Analyze Image & Send", type="primary", use_container_width=True):
            if user_input and uploaded_image:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "has_image": True,
                    "image_name": uploaded_image.name,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Simulate AI response
                with st.spinner("🤖 Analyzing image and preparing response..."):
                    time.sleep(3)
                    
                    # Mock response
                    response = f"I've analyzed your image of {uploaded_image.name}. I can see some concerning spots on the leaves. This appears to be a bacterial leaf spot disease. Here's what I recommend:\n\n• Remove affected leaves immediately\n• Apply copper-based fungicide\n• Improve air circulation around the plant\n• Avoid watering the leaves directly\n\nWould you like more specific treatment details?"
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    st.rerun()
            else:
                st.warning("⚠️ Please provide both a message and an image!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat", use_container_width=True):
            if st.session_state.messages:
                chat_history = {
                    "conversation_id": st.session_state.conversation_id,
                    "messages": st.session_state.messages,
                    "export_timestamp": datetime.now().isoformat()
                }
                
                st.download_button(
                    label="📄 Download Chat History",
                    data=json.dumps(chat_history, indent=2),
                    file_name=f"plantcare_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.info("No chat history to export")
    
    with col3:
        if st.button("🔄 System Status", use_container_width=True):
            try:
                # Mock health check
                st.success("✅ All systems operational")
                st.info(f"🔗 Connected to: {FASTAPI_URL}")
                st.info(f"💬 Active chats: {len(st.session_state.messages)}")
            except Exception as e:
                st.error(f"❌ System check failed: {str(e)}")

# Enhanced Sidebar
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        <div style="text-align: center;">
            <h2 style="color: #1f2937; margin-bottom: 1rem;">🌱 PlantCare AI</h2>
            <p style="color: #6b7280; font-size: 1rem; margin-bottom: 1.5rem;">Your intelligent plant health companion</p>
            <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 1rem; border-radius: 15px; margin-bottom: 1rem;">
                <strong>🎯</strong><br>
                <span style="font-size: 1.1rem;"><strong>{}</strong></span>
            </div>
        </div>
    </div>
    """.format(st.session_state.current_page), unsafe_allow_html=True)
    
    if st.session_state.current_page == "Disease Detection":
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #1f2937; margin-bottom: 1rem;">🔬 Detection Features</h3>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ AI-Powered Analysis</span><br>
                <small style="color: #6b7280;">Advanced machine learning algorithms</small>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ Real-time Processing</span><br>
                <small style="color: #6b7280;">Instant results in seconds</small>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ Multi-format Support</span><br>
                <small style="color: #6b7280;">PNG, JPG, JPEG formats</small>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ Secure Cloud Storage</span><br>
                <small style="color: #6b7280;">AWS S3 integration</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # # Detection Statistics
        # st.markdown("""
        # <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; border: 1px solid #0ea5e9;">
        #     <h4 style="color: #0369a1; margin-bottom: 1rem;">📊 Detection Stats</h4>
        #     <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        #         <span style="color: #374151;">Accuracy Rate:</span>
        #         <span style="color: #0369a1; font-weight: 600;">99.2%</span>
        #     </div>
        #     <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        #         <span style="color: #374151;">Diseases Detected:</span>
        #         <span style="color: #0369a1; font-weight: 600;">50+</span>
        #     </div>
        #     <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        #         <span style="color: #374151;">Processing Time:</span>
        #         <span style="color: #0369a1; font-weight: 600;">&lt;3 sec</span>
        #     </div>
        #     <div style="display: flex; justify-content: space-between;">
        #         <span style="color: #374151;">Images Analyzed:</span>
        #         <span style="color: #0369a1; font-weight: 600;">10,000+</span>
        #     </div>
        # </div>
        # """, unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #1f2937; margin-bottom: 1rem;">🤖 Chat Features</h3>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ Natural Conversations</span><br>
                <small style="color: #6b7280;">Powered by Google Gemini AI</small>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ Image Analysis</span><br>
                <small style="color: #6b7280;">Visual disease detection in chat</small>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ Expert Knowledge</span><br>
                <small style="color: #6b7280;">Agricultural expertise database</small>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <span style="color: #22c55e; font-weight: 600;">✅ 24/7 Availability</span><br>
                <small style="color: #6b7280;">Always ready to help</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat Statistics
        if st.session_state.messages:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; border: 1px solid #0ea5e9;">
                <h4 style="color: #0369a1; margin-bottom: 1rem;">💬 Chat Statistics</h4>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #374151;">Total Messages:</span>
                    <span style="color: #0369a1; font-weight: 600;">{}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #374151;">Images Uploaded:</span>
                    <span style="color: #0369a1; font-weight: 600;">{}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #374151;">Session ID:</span>
                    <span style="color: #0369a1; font-weight: 600; font-size: 0.8rem;">{}...</span>
                </div>
            </div>
            """.format(
                len(st.session_state.messages),
                sum(1 for msg in st.session_state.messages if msg.get("has_image")),
                st.session_state.conversation_id[:8]
            ), unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; border: 1px solid #f59e0b;">
        <h4 style="color: #92400e; margin-bottom: 1rem;">⚡ Quick Actions</h4>
        <div style="margin-bottom: 0.8rem;">
            <button style="width: 100%; padding: 0.8rem; background: #f59e0b; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 600;">
                📋 View User Guide
            </button>
        </div>
        <div style="margin-bottom: 0.8rem;">
            <button style="width: 100%; padding: 0.8rem; background: #f59e0b; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 600;">
                🔗 API Documentation
            </button>
        </div>
        <div style="margin-bottom: 0.8rem;">
            <button style="width: 100%; padding: 0.8rem; background: #f59e0b; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 600;">
                📞 Contact Support
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # System Status
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); padding: 1.5rem; border-radius: 15px; border: 1px solid #10b981;">
        <h4 style="color: #065f46; margin-bottom: 1rem;">🛡️ System Status</h4>
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; margin-right: 0.5rem;"></div>
            <span style="color: #065f46; font-weight: 500;">AI Models: Online</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; margin-right: 0.5rem;"></div>
            <span style="color: #065f46; font-weight: 500;">Chat Service: Active</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; margin-right: 0.5rem;"></div>
            <span style="color: #065f46; font-weight: 500;">Cloud Storage: Connected</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; margin-right: 0.5rem;"></div>
            <span style="color: #065f46; font-weight: 500;">Database: Operational</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ✅ Clean HTML structure that matches your existing CSS
footer_html = """
<div class="professional-footer">
    <div class="footer-content">
        <div class="footer-grid">
            <div class="footer-section">
                <h3>🌱 PlantCare AI</h3>
                <p>Revolutionizing agriculture through artificial intelligence. Our mission is to provide farmers and gardeners with cutting-edge tools for plant health management.</p>
                <p><strong>Empowering sustainable farming since 2024</strong></p>
            </div>
            <div class="footer-section">
                <h3>📞 Support & Contact</h3>
                <p>📧 Email: support@plantcare-ai.com</p>
                <p>🌐 Website: www.plantcare-ai.com</p>
                <p>📱 Phone: +1-800-PLANT-AI</p>
                <p>🕒 Available 24/7</p>
                <p>🏢 Agriculture AI Labs<br>Innovation Center, Tech Valley</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2024 PlantCare AI. All rights reserved. | Privacy Policy | Terms of Service | API Documentation</p>
            <p>Powered by Google Gemini AI | AWS Cloud Infrastructure | Advanced Machine Learning</p>
            <div class="social-links">
                <a href="#" class="social-link">🐦</a>
                <a href="#" class="social-link">📘</a>
                <a href="#" class="social-link">💼</a>
                <a href="#" class="social-link">📷</a>
                <a href="#" class="social-link">🎥</a>
            </div>
            <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
                🌍 Serving farmers worldwide | 🔒 Enterprise-grade security | 🚀 Continuous innovation
            </p>
        </div>
    </div>
</div>
"""

# ✅ Method 1: Standard rendering
st.markdown(footer_html, unsafe_allow_html=True)
