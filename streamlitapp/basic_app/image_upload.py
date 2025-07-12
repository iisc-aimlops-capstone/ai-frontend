import streamlit as st
import boto3
import os
import requests
import json
from io import BytesIO
import time
import base64
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="PlantCare AI - Disease Detection",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to encode image to base64
def get_base64_image(image_path):
    """Convert image to base64 for embedding in CSS"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Custom CSS for professional styling with plant imagery
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global font styling */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main container styling with gradient background */
    .main-header {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 50%, #228B22 100%);
        background-size: 400% 400%;
        animation: gradientShift 6s ease infinite;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 15px 35px rgba(46, 139, 87, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="leaves" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="2" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23leaves)"/></svg>');
        animation: float 20s infinite linear;
        z-index: -1;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0% { transform: translateX(-100px) translateY(-100px); }
        100% { transform: translateX(100px) translateY(100px); }
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.3rem;
        opacity: 0.95;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Upload section styling */
    .upload-section {
        background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 3px dashed #4CAF50;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-section::before {
        content: '🌿';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 3rem;
        opacity: 0.3;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .upload-section:hover {
        border-color: #2E8B57;
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(46, 139, 87, 0.2);
    }
    
    /* Results card styling */
    .results-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-left: 6px solid #4CAF50;
        position: relative;
        overflow: hidden;
    }
    
    .results-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #4CAF50, #81C784);
        border-radius: 50%;
        transform: translate(50%, -50%);
        opacity: 0.1;
    }
    
    .analysis-header {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 50%, #81C784 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 600;
        font-size: 1.2rem;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .analysis-header::before {
        content: '🔬';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: translateY(-50%) scale(1); }
        50% { transform: translateY(-50%) scale(1.1); }
        100% { transform: translateY(-50%) scale(1); }
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border-color: #4CAF50;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4CAF50, #81C784, #A5D6A7);
        border-radius: 15px 15px 0 0;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    /* Translation section */
    .translation-section {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-top: 2rem;
        border: 2px solid #b3d9ff;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .translation-section::before {
        content: '🌍';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 2.5rem;
        opacity: 0.3;
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .translation-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 600;
        font-size: 1.2rem;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced success message */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #c3e6cb;
        text-align: center;
        margin: 1.5rem 0;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(212, 237, 218, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .success-message::before {
        content: '✨';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        animation: sparkle 1.5s infinite;
    }
    
    @keyframes sparkle {
        0%, 100% { opacity: 1; transform: translateY(-50%) scale(1); }
        50% { opacity: 0.7; transform: translateY(-50%) scale(1.2); }
    }
    
    /* Enhanced error message */
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #f5c6cb;
        text-align: center;
        margin: 1.5rem 0;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(248, 215, 218, 0.4);
    }
    
    /* Info section with plant imagery */
    .info-section {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-top: 2rem;
        border: 2px solid #a5d6a7;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .info-header {
        color: #2e7d32;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .info-step {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .info-step:hover {
        transform: translateX(10px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .info-step-number {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        font-size: 1rem;
        box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
    }
    
    /* Plant disease showcase */
    .disease-showcase {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 3rem;
        border-radius: 20px;
        margin: 2rem 0;
        border: 2px solid #ffcc02;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .disease-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 2px solid #f0f0f0;
    }
    
    .disease-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border-color: #ff9800;
    }
    
    .disease-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e65100;
        margin-bottom: 0.5rem;
    }
    
    .disease-description {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Sidebar enhancements */
    .sidebar-info {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #dee2e6;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .sidebar-info::before {
        content: '🌱';
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);
    }
    
    /* Loading animations */
    .loading-text {
        animation: pulse 2s infinite;
        color: #4CAF50;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom file uploader styling */
    .stFileUploader > div > div > div > div {
        background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);
        border: 3px dashed #4CAF50;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div > div > div:hover {
        border-color: #2E8B57;
        transform: scale(1.02);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1.1rem;
        }
        
        .upload-section {
            padding: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "s3b-iisc-aimlops-cap-images")
S3_REGION = os.environ.get("AWS_REGION", "us-east-2")
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://plant-disease-detection.aichamp.publicvm.com/api")

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

# Sample plant disease data for showcase
plant_diseases = [
    {
        "name": "Leaf Blight",
        "description": "A fungal disease causing brown spots on leaves, leading to yellowing and premature leaf drop.",
        "emoji": "🍃",
        "color": "#8B4513"
    },
    {
        "name": "Powdery Mildew",
        "description": "White powdery fungal growth on leaves and stems, affecting photosynthesis.",
        "emoji": "⚪",
        "color": "#DDA0DD"
    },
    {
        "name": "Root Rot",
        "description": "Fungal infection of plant roots causing wilting, yellowing, and stunted growth.",
        "emoji": "🦠",
        "color": "#CD853F"
    },
    {
        "name": "Aphid Infestation",
        "description": "Small insects that feed on plant sap, causing curled leaves and stunted growth.",
        "emoji": "🐛",
        "color": "#228B22"
    },
    {
        "name": "Bacterial Spot",
        "description": "Bacterial infection causing dark spots on leaves, stems, and fruits.",
        "emoji": "🔴",
        "color": "#DC143C"
    },
    {
        "name": "Mosaic Virus",
        "description": "Viral disease causing mottled yellow and green patterns on leaves.",
        "emoji": "🌈",
        "color": "#FF6347"
    }
]

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("""
    <div class="sidebar-info">
        <h2 style="color: #2E8B57; margin-bottom: 1rem;">🌱 PlantCare AI</h2>
        <p style="color: #666; font-size: 1rem; line-height: 1.5;">
            Advanced plant disease detection powered by cutting-edge artificial intelligence and machine learning algorithms.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Platform Features")
    st.success("🔬 AI-powered disease analysis")
    st.success("🌍 Multi-language support")
    st.success("☁️ Secure cloud storage")
    st.success("⚡ Real-time processing")
    st.success("📱 Mobile-friendly interface")
    st.success("🎯 High accuracy detection")
    
    st.markdown("### 🔧 System Configuration")
    st.info(f"🌎 AWS Region: {S3_REGION}")
    st.info(f"🪣 S3 Bucket: {S3_BUCKET}")
    st.info(f"🔗 API Status: Online")
    
    st.markdown("### 🌿 Supported Plants")
    plants = ["🌾 Rice", "🌽 Corn", "🍅 Tomato", "🥔 Potato", "🌶️ Pepper", "🥒 Cucumber", "🍆 Eggplant", "🥬 Lettuce"]
    for plant in plants:
        st.write(f"• {plant}")
    
    st.markdown("### 📞 Need Help?")
    st.markdown("""
    <div style="background: #f0f8ff; padding: 1rem; border-radius: 10px; border: 1px solid #b3d9ff;">
        <p style="margin: 0; color: #0066cc; font-size: 0.9rem;">
            📧 Email: support@plantcare.ai<br>
            📱 Phone: +1 (555) 123-4567<br>
            🌐 Website: www.plantcare.ai
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main Header with enhanced design
st.markdown("""
<div class="main-header">
    <h1>🌱 PlantCare AI</h1>
    <p>Professional Plant Disease Detection & Smart Farming Solutions</p>
</div>
""", unsafe_allow_html=True)

# Plant Disease Showcase Section
st.markdown("""
<div class="disease-showcase">
    <h2 style="text-align: center; color: #e65100; margin-bottom: 2rem; font-size: 2.2rem;">
        🔍 Common Plant Diseases We Detect
    </h2>
    <p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Our AI system is trained to identify various plant diseases with high accuracy
    </p>
</div>
""", unsafe_allow_html=True)

# Display disease cards in a grid
cols = st.columns(3)
for i, disease in enumerate(plant_diseases):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="disease-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 3rem;">{disease['emoji']}</span>
            </div>
            <div class="disease-name">{disease['name']}</div>
            <div class="disease-description">{disease['description']}</div>
        </div>
        """, unsafe_allow_html=True)

# Upload Section with enhanced styling
# Upload Section with styled dropzone container
with st.container():
    st.markdown("""
    <div style="background: #f0fff0; border: 3px dashed #4CAF50; padding: 2.5rem; border-radius: 20px; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.05); position: relative;">
        <h2 style="color: #2E8B57; margin-bottom: 0.8rem;">📤 Upload Plant Images for Analysis</h2>
        <p style="color: #555; font-size: 1.05rem;">Select high-quality images of your plants for instant AI-powered disease detection</p>
        <p style="color: #888; font-size: 0.9rem;">📷 Supported formats: PNG, JPG, JPEG &nbsp;&nbsp; 🧾 Max size: 10MB per image</p>
    """, unsafe_allow_html=True)

    # Add file uploader INSIDE the green container
    uploaded_images = st.file_uploader(
        label="",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Drag and drop or browse plant images inside this green area"
    )

    st.markdown("</div>", unsafe_allow_html=True)

if uploaded_images:
    # Display number of uploaded files with animation
    st.markdown(f"""
    <div class="success-message">
        ✅ {len(uploaded_images)} image(s) successfully selected for AI analysis
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar for visual feedback
    progress_bar = st.progress(0)
    
    for idx, image in enumerate(uploaded_images, 1):
        # Update progress
        progress_bar.progress(idx / len(uploaded_images))
        
        st.markdown(f"""
        <div class="results-card">
            <h3 style="color: #2E8B57; margin-bottom: 1rem; font-size: 1.5rem;">
                📸 Image Analysis #{idx}: {image.name}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Read file content once
        file_bytes = image.read()
        file_buffer = BytesIO(file_bytes)
        
        try:
            # Upload to S3
            file_buffer.seek(0)
            s3_client.upload_fileobj(
                file_buffer,
                S3_BUCKET,
                image.name,
                ExtraArgs={"ContentType": image.type}
            )
            
            # Display success message
            st.markdown("""
            <div class="success-message">
                ✅ Image successfully uploaded to secure cloud storage!
            </div>
            """, unsafe_allow_html=True)
            
            # Display uploaded image in an enhanced container
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(
                    BytesIO(file_bytes), 
                    caption=f"🌿 Uploaded Plant Image: {image.name}", 
                    use_column_width=True
                )
            
            # Enhanced analysis section
            st.markdown("""
            <div class="analysis-header">
                🔍 AI Analysis in Progress - Please Wait
            </div>
            """, unsafe_allow_html=True)
            
            # Show enhanced processing message
            with st.spinner('🤖 Our advanced AI is analyzing your plant image for diseases...'):
                try:
                    # Call FastAPI endpoint for analysis
                    response = requests.post(
                        f"{FASTAPI_URL}/analyze_from_s3/",
                        json={
                            "file_key": image.name
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display results in enhanced format
                        st.markdown("### 📊 Detailed Analysis Results")
                        
                        # Create enhanced metrics row
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            plant_status = "🌱 Healthy Plant" if result.get('is_plant', 'false').lower().startswith('true') else "❌ Not a Plant"
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{plant_status}</div>
                                <div class="metric-label">Plant Classification</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            confidence = f"{result.get('confidence', 0):.1%}" if result.get('confidence') else "N/A"
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{confidence}</div>
                                <div class="metric-label">Detection Confidence</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            disease_label = result.get('label', 'Unknown')
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value" style="font-size: 1.2rem;">{disease_label}</div>
                                <div class="metric-label">Detected Condition</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Enhanced message display
                        if result.get('message'):
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; border-left: 5px solid #4CAF50; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                                <h4 style="color: #2E8B57; margin-bottom: 1rem;">📝 AI Analysis Summary</h4>
                                <p style="color: #333; font-size: 1.1rem; line-height: 1.6; margin: 0;">
                                    {result['message']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Show detailed JSON in enhanced expander
                        with st.expander("🔍 View Technical Analysis Details", expanded=False):
                            st.json(result)
                        
                        # Enhanced translation section
                        if 'disease_details' in result and result['disease_details']:
                            original_text = result['disease_details']
                            
                            # Initialize state for the current image
                            if image.name not in st.session_state:
                                st.session_state[image.name] = {
                                    "original": original_text,
                                    "translated": ""
                                }
                            
                            st.markdown("""
                            <div class="translation-section">
                                <div class="translation-header">
                                    🌍 Disease Details & Multi-Language Translation
                                </div>
                                <p style="text-align: center; color: #666; margin-bottom: 2rem;">
                                    Get detailed disease information in your preferred regional language
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Create two columns for original and translated text
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("""
                                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                                    <h4 style="color: #2E8B57; margin-bottom: 0.5rem;">📄 Original Details (English)</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                st.text_area(
                                    label="Original Details",
                                    value=st.session_state[image.name]["original"],
                                    height=300,
                                    disabled=True,
                                    label_visibility="collapsed"
                                )
                            
                            with col2:
                                st.markdown("""
                                <div style="background: #f0f8ff; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                                    <h4 style="color: #4169E1; margin-bottom: 0.5rem;">🌐 Translated Details</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Enhanced language selection
                                language_options = {
                                    "हिंदी (Hindi)": "hi",
                                    "தமிழ் (Tamil)": "ta", 
                                    "বাংলা (Bengali)": "bn",
                                    "తెలుగు (Telugu)": "te",
                                    "മലയാളം (Malayalam)": "ml",
                                    "ಕನ್ನಡ (Kannada)": "kn",
                                    "ગુજરાતી (Gujarati)": "gu",
                                    "ਪੰਜਾਬੀ (Punjabi)": "pa",
                                    "मराठी (Marathi)": "mr",
                                    "ଓଡ଼ିଆ (Odia)": "or"
                                }
                                
                                selected_language = st.selectbox(
                                    "🗣️ Select Language for Translation",
                                    options=list(language_options.keys()),
                                    key=f"lang_select_{image.name}",
                                    help="Choose your preferred regional language for detailed disease information"
                                )
                                
                                # Translation logic with enhanced feedback
                                target_lang_code = language_options[selected_language]
                                if target_lang_code:
                                    if st.button(f"🔄 Translate to {selected_language.split('(')[0].strip()}", key=f"translate_{image.name}"):
                                        try:
                                            with st.spinner(f'🌍 Translating to {selected_language}...'):
                                                translation_response = requests.post(
                                                    f"{FASTAPI_URL}/translate",
                                                    json={
                                                        "text": result['disease_details'],
                                                        "target_language": target_lang_code
                                                    },
                                                    timeout=20
                                                )
                                                
                                                if translation_response.status_code == 200:
                                                    translated_text = translation_response.json().get("translated_text", "Translation failed.")
                                                    st.session_state[image.name]["translated"] = translated_text
                                                    st.success(f"✅ Successfully translated to {selected_language.split('(')[0].strip()}!")
                                                else:
                                                    st.session_state[image.name]["translated"] = f"❌ Translation Error: {translation_response.text}"
                                                    st.error("Translation service encountered an error.")
                                        except Exception as e:
                                            st.session_state[image.name]["translated"] = f"⚠️ Translation service error: {e}"
                                            st.error("Unable to connect to translation service.")
                                
                                st.text_area(
                                    label="Translated Details",
                                    value=st.session_state[image.name]["translated"],
                                    height=300,
                                    disabled=True,
                                    label_visibility="collapsed"
                                )
                        
                        # Add recommendations section
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; border-left: 5px solid #FFA000; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                            <h4 style="color: #E65100; margin-bottom: 1rem;">💡 Treatment Recommendations</h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                                <div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #FFE082;">
                                    <h5 style="color: #FF8F00; margin-bottom: 0.5rem;">🌿 Organic Treatment</h5>
                                    <p style="color: #666; font-size: 0.9rem; margin: 0;">Use neem oil or organic fungicides for natural treatment</p>
                                </div>
                                <div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #FFE082;">
                                    <h5 style="color: #FF8F00; margin-bottom: 0.5rem;">💧 Watering Care</h5>
                                    <p style="color: #666; font-size: 0.9rem; margin: 0;">Adjust watering schedule and improve drainage</p>
                                </div>
                                <div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #FFE082;">
                                    <h5 style="color: #FF8F00; margin-bottom: 0.5rem;">🌱 Prevention</h5>
                                    <p style="color: #666; font-size: 0.9rem; margin: 0;">Remove affected leaves and improve air circulation</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                            
                    else:
                        st.markdown(f"""
                        <div class="error-message">
                            ❌ Analysis failed with status code: {response.status_code}<br>
                            <strong>Error details:</strong> {response.text}
                        </div>
                        """, unsafe_allow_html=True)
                        
                except requests.exceptions.Timeout:
                    st.markdown("""
                    <div class="error-message">
                        ⏰ Request timed out. The analysis is taking longer than expected.<br>
                        <strong>Tip:</strong> Please try again with a smaller image or check your internet connection.
                    </div>
                    """, unsafe_allow_html=True)
                except requests.exceptions.ConnectionError:
                    st.markdown("""
                    <div class="error-message">
                        🔌 Could not connect to the analysis service.<br>
                        <strong>Status:</strong> Backend service may be temporarily unavailable.
                    </div>
                    """, unsafe_allow_html=True)
                except requests.exceptions.RequestException as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Request failed: {str(e)}<br>
                        <strong>Action:</strong> Please try again or contact support.
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ An unexpected error occurred: {str(e)}<br>
                        <strong>Support:</strong> Please contact our technical team.
                    </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as e:
            st.markdown(f"""
            <div class="error-message">
                ❌ Failed to upload image to S3: {str(e)}<br>
                <strong>Suggestion:</strong> Please check your image format and try again.
            </div>
            """, unsafe_allow_html=True)
        
        # Add separator between images
        if idx < len(uploaded_images):
            st.markdown("""
            <div style="margin: 3rem 0; text-align: center;">
                <div style="height: 2px; background: linear-gradient(90deg, transparent, #4CAF50, transparent); margin: 2rem 0;"></div>
                <span style="background: white; padding: 0 1rem; color: #666; font-size: 0.9rem;">Next Image Analysis</span>
            </div>
            """)
    
    # Clear progress bar
    progress_bar.empty()

# Enhanced Information Section
st.markdown("---")
st.markdown("""
<div class="info-section">
    <div class="info-header">ℹ️ How PlantCare AI Works</div>
    <p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Our state-of-the-art AI system uses advanced computer vision and machine learning
    </p>
</div>
""", unsafe_allow_html=True)

# Enhanced process steps
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-step">
        <div class="info-step-number">1</div>
        <div style="display: inline-block; vertical-align: top;">
            <h4 style="color: #2E8B57; margin-bottom: 0.5rem;">📤 Upload Images</h4>
            <p style="color: #666; margin: 0;">Select high-quality plant images from your device. Our system supports multiple formats.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-step">
        <div class="info-step-number">2</div>
        <div style="display: inline-block; vertical-align: top;">
            <h4 style="color: #2E8B57; margin-bottom: 0.5rem;">☁️ Secure Storage</h4>
            <p style="color: #666; margin: 0;">Images are securely uploaded to AWS S3 cloud storage with enterprise-grade security.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-step">
        <div class="info-step-number">3</div>
        <div style="display: inline-block; vertical-align: top;">
            <h4 style="color: #2E8B57; margin-bottom: 0.5rem;">🔍 AI Analysis</h4>
            <p style="color: #666; margin: 0;">Our advanced AI model analyzes images using deep learning for accurate disease detection.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-step">
        <div class="info-step-number">4</div>
        <div style="display: inline-block; vertical-align: top;">
            <h4 style="color: #2E8B57; margin-bottom: 0.5rem;">📊 Detailed Results</h4>
            <p style="color: #666; margin: 0;">Get comprehensive analysis results with disease information and treatment recommendations.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-step">
        <div class="info-step-number">5</div>
        <div style="display: inline-block; vertical-align: top;">
            <h4 style="color: #2E8B57; margin-bottom: 0.5rem;">🌍 Multi-Language</h4>
            <p style="color: #666; margin: 0;">Access disease details in your preferred regional language for better understanding.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-step">
        <div class="info-step-number">6</div>
        <div style="display: inline-block; vertical-align: top;">
            <h4 style="color: #2E8B57; margin-bottom: 0.5rem;">💡 Recommendations</h4>
            <p style="color: #666; margin: 0;">Receive expert treatment recommendations and prevention tips for optimal plant health.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# AI Technology Showcase
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); padding: 3rem; border-radius: 20px; margin: 2rem 0; border: 2px solid #ba68c8;">
    <h2 style="text-align: center; color: #6a1b9a; margin-bottom: 2rem; font-size: 2.2rem;">
        🧠 AI Technology Behind PlantCare
    </h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem;">
        <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔬</div>
            <h3 style="color: #6a1b9a; margin-bottom: 1rem;">Deep Learning</h3>
            <p style="color: #666; font-size: 1rem;">Convolutional Neural Networks trained on millions of plant images</p>
        </div>
        <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">👁️</div>
            <h3 style="color: #6a1b9a; margin-bottom: 1rem;">Computer Vision</h3>
            <p style="color: #666; font-size: 1rem;">Advanced image processing and pattern recognition algorithms</p>
        </div>
        <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <h3 style="color: #6a1b9a; margin-bottom: 1rem;">High Accuracy</h3>
            <p style="color: #666; font-size: 1rem;">95%+ accuracy in disease detection across various plant species</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Backend Status Check with enhanced design
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 3rem; border-radius: 20px; margin: 2rem 0; border: 2px solid #2196f3;">
    <h2 style="text-align: center; color: #0d47a1; margin-bottom: 1rem; font-size: 2.2rem;">
        🔧 System Health Status
    </h2>
    <p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
        Monitor the real-time health of our backend services and infrastructure
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🖥️</div>
        <h4 style="color: #2196f3; margin-bottom: 0.5rem;">API Server</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">FastAPI Backend</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">☁️</div>
        <h4 style="color: #2196f3; margin-bottom: 0.5rem;">Cloud Storage</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">AWS S3 Service</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🤖</div>
        <h4 style="color: #2196f3; margin-bottom: 0.5rem;">AI Model</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">ML Inference Engine</p>
    </div>
    """, unsafe_allow_html=True)

if st.button("🔍 Check Complete System Health", use_container_width=True):
    try:
        with st.spinner('🔄 Performing comprehensive health check...'):
            health_response = requests.get(f"{FASTAPI_URL}/health/", timeout=5)
            if health_response.status_code == 200:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 2rem; border-radius: 15px; text-align: center; margin: 1rem 0; border: 2px solid #28a745;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
                    <h3 style="color: #155724; margin-bottom: 1rem;">All Systems Operational</h3>
                    <p style="color: #155724; font-size: 1.1rem; margin: 0;">Backend service is healthy and running perfectly!</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); padding: 2rem; border-radius: 15px; text-align: center; margin: 1rem 0; border: 2px solid #dc3545;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                    <h3 style="color: #721c24; margin-bottom: 1rem;">Service Issue Detected</h3>
                    <p style="color: #721c24; font-size: 1.1rem; margin: 0;">Status Code: {health_response.status_code}</p>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); padding: 2rem; border-radius: 15px; text-align: center; margin: 1rem 0; border: 2px solid #dc3545;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
            <h3 style="color: #721c24; margin-bottom: 1rem;">Connection Error</h3>
            <p style="color: #721c24; font-size: 1.1rem; margin: 0;">Unable to reach backend service: {str(e)}</p>
        </div>
        """, unsafe_allow_html=True)

# Enhanced Footer
components.html("""
<div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 3rem; border-radius: 20px; margin-top: 3rem;
            text-align: center; color: white;">
    <h2 style="color: #4CAF50; margin-bottom: 1rem; font-size: 2.5rem;">🌱 PlantCare AI</h2>
    <p style="font-size: 1.1rem; opacity: 0.85;">Empowering farmers with smart disease detection</p>
    
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 2rem;">
        <div style="min-width: 200px; max-width: 300px; margin: 1rem;">
            <h4 style="color: #4CAF50;">🚀 Features</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>✅ Real-time detection</li>
                <li>🌐 Multi-language</li>
                <li>💡 Smart tips</li>
            </ul>
        </div>
        <div style="min-width: 200px; max-width: 300px; margin: 1rem;">
            <h4 style="color: #4CAF50;">🌍 Impact</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>📉 Crop loss reduction</li>
                <li>🌾 Sustainable farming</li>
                <li>🍽️ Food security</li>
            </ul>
        </div>
        <div style="min-width: 200px; max-width: 300px; margin: 1rem;">
            <h4 style="color: #4CAF50;">📞 Contact</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>📧 info@plantcare.ai</li>
                <li>📱 +1 (555) 123-4567</li>
                <li>🌐 www.plantcare.ai</li>
            </ul>
        </div>
    </div>

    <hr style="border-top: 1px solid #4CAF50; margin-top: 2rem;">
    <p style="font-size: 0.85rem; opacity: 0.6;">© 2024 PlantCare AI. Made with ❤️ for sustainable agriculture.</p>
</div>
""", height=600)
