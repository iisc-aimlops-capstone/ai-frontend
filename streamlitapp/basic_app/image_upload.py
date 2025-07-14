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

# Page Configuration
st.set_page_config(
    page_title="PlantCare AI - Disease Detection & Chat Assistant",
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

# Custom CSS (keeping your existing styles plus chatbot styles)
st.markdown("""
<style>
    /* Your existing CSS styles here... */
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global font styling */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Chatbot specific styles */
    .chat-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        max-height: 600px;
        overflow-y: auto;
        border: 2px solid #dee2e6;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .chat-message {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 15px;
        max-width: 80%;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        margin-left: auto;
        text-align: right;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #333;
        margin-right: auto;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .chat-input-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 2px solid #4CAF50;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.2);
    }
    
    .chat-header {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
    }
    
    .chat-header h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .chat-features {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #a5d6a7;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        color: #2e7d32;
        font-weight: 500;
    }
    
    .feature-item::before {
        content: "✅";
        margin-right: 0.5rem;
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        color: #666;
        font-style: italic;
        margin: 1rem 0;
    }
    
    .typing-dots {
        margin-left: 0.5rem;
    }
    
    .typing-dots span {
        animation: typing 1.4s infinite;
        animation-fill-mode: both;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0); }
    }
    
    /* Page navigation */
    .page-nav {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .nav-button {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 0.8rem 1.5rem;
        margin: 0 0.5rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
    }
    
    .nav-button.active {
        background: white;
        color: #2E8B57;
        border-color: white;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .chat-message {
            max-width: 95%;
        }
        
        .nav-button {
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Navigation
st.markdown("""
<div class="page-nav">
    <h3 style="color: white; margin-bottom: 1rem;">🌱 PlantCare AI Navigation</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Disease Detection", key="nav_detection", use_container_width=True):
        st.session_state.current_page = "Disease Detection"
with col2:
    if st.button("🤖 AI Chat Assistant", key="nav_chat", use_container_width=True):
        st.session_state.current_page = "Chat Assistant"

# Main content based on selected page
if st.session_state.current_page == "Disease Detection":
    # Your existing disease detection code goes here
    # I'll include the key parts...
    
    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1>🌱 PlantCare AI - Disease Detection</h1>
        <p>Professional Plant Disease Detection & Smart Farming Solutions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload Section
    with st.container():
        st.markdown("""
        <div style="background: #f0fff0; border: 3px dashed #4CAF50; padding: 2.5rem; border-radius: 20px; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.05);">
            <h2 style="color: #2E8B57; margin-bottom: 0.8rem;">📤 Upload Plant Images for Analysis</h2>
            <p style="color: #555; font-size: 1.05rem;">Select high-quality images of your plants for instant AI-powered disease detection</p>
        """, unsafe_allow_html=True)
        
        uploaded_images = st.file_uploader(
            label="",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Process uploaded images (your existing code)
    if uploaded_images:
        st.success(f"✅ {len(uploaded_images)} image(s) uploaded successfully!")
        # ... rest of your existing image processing code ...

elif st.session_state.current_page == "Chat Assistant":
    # Chatbot Interface
    st.markdown("""
    <div class="chat-header">
        <h2>🤖 PlantCare AI Chat Assistant</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Get instant answers about plant diseases, treatments, and care tips</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat features
    st.markdown("""
    <div class="chat-features">
        <h3 style="color: #2e7d32; margin-bottom: 1rem;">🌟 What I Can Help With:</h3>
        <div class="feature-item">Disease identification from symptoms</div>
        <div class="feature-item">Treatment recommendations and remedies</div>
        <div class="feature-item">Prevention strategies and plant care tips</div>
        <div class="feature-item">Organic and eco-friendly solutions</div>
        <div class="feature-item">Plant health monitoring advice</div>
        <div class="feature-item">Image analysis with detailed diagnosis</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                    {f'<br><em>📷 Image: {message.get("image_name", "uploaded")}</em>' if message.get("has_image") else ""}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🌱 PlantCare AI:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input section
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Choose input type
    input_type = st.radio(
        "Choose input method:",
        ["💬 Text Only", "📷 Text + Image"],
        horizontal=True
    )
    
    if input_type == "💬 Text Only":
        # Text-only chat
        user_input = st.text_input(
            "Ask me anything about plant diseases and care:",
            placeholder="e.g., My tomato leaves are turning yellow with brown spots...",
            key="text_input"
        )
        
        if st.button("💬 Send Message", key="send_text", use_container_width=True):
            if user_input:
                # Add user message to chat
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Show typing indicator
                with st.spinner("🤖 PlantCare AI is thinking..."):
                    try:
                        # Call FastAPI text chat endpoint
                        response = requests.post(
                            f"{FASTAPI_URL}/chat/text",
                            json={
                                "message": user_input,
                                "conversation_history": [
                                    {"user": msg["content"], "assistant": ""}
                                    for msg in st.session_state.messages[-5:]
                                    if msg["role"] == "user"
                                ]
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Add assistant response to chat
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["response"],
                                "timestamp": result["timestamp"]
                            })
                            
                            # Update conversation ID
                            st.session_state.conversation_id = result["conversation_id"]
                            
                            st.rerun()
                        else:
                            st.error(f"Chat service error: {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    else:
        # Text + Image chat
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_input = st.text_area(
                "Describe your plant issue:",
                placeholder="e.g., I found these spots on my plant leaves. What could be causing this?",
                height=100
            )
        
        with col2:
            uploaded_image = st.file_uploader(
                "Upload plant image:",
                type=["png", "jpg", "jpeg"],
                key="chat_image"
            )
        
        if st.button("📷 Send Message with Image", key="send_image", use_container_width=True):
            if user_input and uploaded_image:
                # Add user message to chat
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "has_image": True,
                    "image_name": uploaded_image.name,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Show typing indicator
                with st.spinner("🤖 Analyzing image and preparing response..."):
                    try:
                        # Prepare form data
                        files = {"image": (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)}
                        data = {
                            "message": user_input,
                            "conversation_history": json.dumps([
                                {"user": msg["content"], "assistant": ""}
                                for msg in st.session_state.messages[-5:]
                                if msg["role"] == "user"
                            ])
                        }
                        
                        # Call FastAPI image chat endpoint
                        response = requests.post(
                            f"{FASTAPI_URL}/chat/image",
                            files=files,
                            data=data,
                            timeout=45
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Add assistant response to chat
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["response"],
                                "timestamp": result["timestamp"]
                            })
                            
                            # Update conversation ID
                            st.session_state.conversation_id = result["conversation_id"]
                            
                            st.rerun()
                        else:
                            st.error(f"Image chat service error: {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please provide both message and image!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()
    
    with col2:
        if st.button("💾 Save Chat", key="save_chat"):
            # Create downloadable chat history
            chat_history = {
                "conversation_id": st.session_state.conversation_id,
                "messages": st.session_state.messages,
                "timestamp": datetime.now().isoformat()
            }
            
            st.download_button(
                label="📄 Download Chat History",
                data=json.dumps(chat_history, indent=2),
                file_name=f"plantcare_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🔄 Health Check", key="chat_health"):
            try:
                health_response = requests.get(f"{FASTAPI_URL}/chat/health", timeout=5)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    st.success(f"✅ Chat service is healthy! Active conversations: {health_data['active_conversations']}")
                else:
                    st.error("❌ Chat service health check failed")
            except Exception as e:
                st.error(f"❌ Health check error: {str(e)}")

# Sidebar enhancements
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: #2E8B57; margin-bottom: 1rem;">🌱 PlantCare AI</h2>
        <p style="color: #666; font-size: 1rem;">Your intelligent plant health companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.current_page == "Chat Assistant":
        st.markdown("### 🤖 Chat Assistant Features")
        st.success("💬 Natural language conversations")
        st.success("📷 Image analysis capability")
        st.success("🧠 Powered by Google Gemini")
        st.success("🌱 Plant disease expertise")
        st.success("💡 Treatment recommendations")
        st.success("🔄 Conversation history")
        
        # Chat statistics
        if st.session_state.messages:
            st.markdown("### 📊 Chat Statistics")
            st.info(f"Messages: {len(st.session_state.messages)}")
            st.info(f"Conversation ID: {st.session_state.conversation_id[:8]}...")
            
            # Count images uploaded
            image_count = sum(1 for msg in st.session_state.messages if msg.get("has_image"))
            st.info(f"Images analyzed: {image_count}")
    
    else:
        st.markdown("### 📊 Disease Detection Features")
        st.success("🔬 AI-powered analysis")
        st.success("🌍 Multi-language support")
        st.success("☁️ Secure cloud storage")
        st.success("⚡ Real-time processing")
        st.success("📱 Mobile-friendly interface")
        st.success("🎯 High accuracy detection")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🌱 PlantCare AI - Empowering farmers with AI-powered plant health solutions</p>
    <p>💡 Now with intelligent chat assistant powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)