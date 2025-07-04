import streamlit as st
import boto3
import os
import requests
import json
from io import BytesIO
import time

st.title("AI - Plant Disease Detection and Farmer Assistance")

# Configuration
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "s3b-iisc-aimlops-cap-images")
S3_REGION = os.environ.get("AWS_REGION", "us-east-2")
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://plant-disease-detection.aichamp.publicvm.com/api")  # Update with your FastAPI URL

# Initialize S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

# File uploader
uploaded_images = st.file_uploader(
    "Upload an image", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if uploaded_images:
    for image in uploaded_images:
        st.write("Filename: ", image.name)
        
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
            st.markdown(
                """
                <div style="border: 2px solid #4CAF50; border-radius: 5px;
                            background-color: #e8f5e8; text-align: center; padding: 10px; margin: 10px 0;">
                    <strong>✅ Image uploaded to S3 successfully!</strong>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Display uploaded image
            st.image(BytesIO(file_bytes), caption="Uploaded Image", width=300)
            
            # Show processing message
            with st.spinner('🔍 Analyzing image for plant disease...'):
                try:
                    # Call FastAPI endpoint for analysis - UPDATED: Only sending file_key
                    response = requests.post(
                        f"{FASTAPI_URL}/analyze_from_s3/",
                        json={
                            "file_key": image.name  # Only file_key needed now
                        },
                        timeout=30  # 30 seconds timeout
                    )
                    
                    if response.status_code == 200:
                        # Parse the JSON response
                        result = response.json()
                        
                        # Display results in a nice format
                        st.markdown("### 📊 Analysis Results")
                        
                        # Create columns for better layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Image Type", "Plant" if result.get('is_plant', 'false').lower().startswith('true') else "Not a Plant")
                        
                        with col2:
                            if result.get('confidence'):
                                st.metric("Confidence", f"{result['confidence']:.2%}")
                        
                        if result.get('label'):
                            st.markdown(f"**🌱 Detected Disease:** {result['label']}")
                        
                        st.markdown(f"**📝 Message:** {result.get('message', 'No message available')}")
                        
                        # Show full JSON response in an expander
                        with st.expander("View Full Analysis Details"):
                            st.json(result)
                            
                    else:
                        st.error(f"❌ Analysis failed with status code: {response.status_code}")
                        st.error(f"Error details: {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏰ Request timed out. The analysis is taking longer than expected.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Could not connect to the analysis service. Please check if the backend is running.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Request failed: {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ Failed to upload image to S3: {str(e)}")

# Add some helpful information
st.markdown("---")
st.markdown("### ℹ️ How it works:")
st.markdown("""
1. **Upload**: Select one or more plant images to upload
2. **Store**: Images are securely stored in AWS S3
3. **Analyze**: Our AI model analyzes the images for plant diseases
4. **Results**: Get detailed information about detected diseases and recommendations
""")

# Health check section
st.markdown("---")
if st.button("🔍 Check Backend Status"):
    try:
        health_response = requests.get(f"{FASTAPI_URL}/health/", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Backend service is healthy and running!")
        else:
            st.warning(f"⚠️ Backend service returned status code: {health_response.status_code}")
    except Exception as e:
        st.error(f"❌ Backend service is not reachable: {str(e)}")