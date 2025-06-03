import streamlit as st
import boto3
import os

st.title("AI - Plant Disease Detection and Farmer Assistance")

# S3 configuration
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "s3b-iisc-aimlops-cap-images")
S3_REGION = os.environ.get("AWS_REGION", "us-east-2")

# Create S3 client (uses IAM role in ECS)
s3_client = boto3.client("s3", region_name=S3_REGION)

uploaded_images = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_images is not None:
    for image in uploaded_images:
        st.write("filename: ", image.name)
        # Upload to S3
        s3_client.upload_fileobj(
            image,
            S3_BUCKET,
            image.name,
            ExtraArgs={"ContentType": image.type}
        )
        st.markdown(
            """
            <div style="border: 2px solid #4CAF50; border-radius: 2px; 
                        background-color: brown; text-align: center;">
                <strong>Image uploaded to S3!</strong>
            </div>
            """, unsafe_allow_html=True)
        st.image(image, caption="Uploaded Image")