import streamlit as st

st.title("AI - Plant Disease Detection and Farmer Assistance")

uploaded_image = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_image is not None:
    for image in uploaded_image:
        # bytes_data = image.read()
        st.write("'filename: ", image.name)
        # st.write(bytes_data)
        st.markdown(
            """
            <div style="border: 2px solid #4CAF50; border-radius: 2px; 
                        background-color: brown; text-align: center;">
                <strong>Image uploaded!</strong>
            </div>
            """, unsafe_allow_html=True)
        st.image(uploaded_image, caption="Uploaded Image")