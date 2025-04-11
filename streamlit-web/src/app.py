import streamlit as st
import os
from utils.drive_utils import authenticate_drive, upload_file_to_drive, get_lists_of_folders
# from utils.compression_utils import compress_video
from utils.download_utils import download_file


def main():
    if not os.path.exists("downloaded-files"):
        os.makedirs("downloaded-files")
        
    def initialize_state(state_name, default_value=None):
        if state_name not in st.session_state:
            st.session_state[state_name] = default_value if default_value is not None else []

    def update_state(state_name, new_value):
        st.session_state[state_name] = new_value
        return st.session_state[state_name]

    initialize_state("list_all_files", os.listdir("downloaded-files"))
    list_all_files = st.session_state.list_all_files

    def refresh_file_list():
        return update_state("list_all_files", os.listdir("downloaded-files"))

    initialize_state("service", None)    
    service = None

    st.title("Video Upload to Google Drive")

    # Request download link
    download_link = st.text_input("Enter the download link for the video:")

    if st.button("Download file"):
        if download_link:
            file_name = download_file(download_link)
            list_all_files = refresh_file_list()
            st.success(f"File downloaded from {download_link}!")
        else:
            st.error("Please enter a valid download link.")

    # Compress selected file
    selected_file = st.selectbox("Select a file to compress:", list_all_files)
    if st.button("Compress Video"):
        if selected_file:
            file_name = f"{os.path.splitext(selected_file)[0]}_compressed{os.path.splitext(selected_file)[1]}"
            file_path = f"downloaded-files/{file_name}"
            with open(file_path, "wb") as f:
                # Simulate writing to file
                f.write(os.urandom(1024))
            st.success(f"File {file_name} compressed successfully!")
        else:
            st.error("Please select a file to compress.")
    
    # Google drive parts
    st.divider()
    st.subheader("Authenticate to Google Drive")

    # Upload token or credentials file
    initialize_state("token_file_path", "temp_credentials.json")
    token_file_path = st.session_state.token_file_path

    initialize_state("token_file_content", None)

    def check_token_file_content():
        if os.path.exists("temp_credentials.json"):
            with open("temp_credentials.json", "r") as f:
                update_state("token_file_content", f.read())
            
            return st.session_state.token_file_content
        
    
    token_file_content = check_token_file_content()
    
    token_file_input = st.file_uploader("Upload token.json or credentials.json", type=["json"])


    if st.button("Upload Token File"):
        if token_file_input is not None:
            # Save the uploaded token file temporarily
            with open("temp_credentials.json", "wb") as f:
                f.write(token_file_input.getbuffer())
            
            token_file_content = check_token_file_content()
                
            st.success("Token file uploaded successfully!")
        else:
            st.error("Please upload a valid token file.")
    
    # Show the content of the uploaded token file
    if st.button("Show/Hide Token File Content"):
        initialize_state("show_token_content", False)

        update_state("show_token_content", not st.session_state.show_token_content)

    if st.session_state.get("show_token_content", False):
        if token_file_content is not None:
            token_file_content = check_token_file_content()
            st.text_area("Token File Content", token_file_content, height=200)
        else:
            st.error("No token file uploaded.")

    # Authenticate Google Drive
    if st.button("Authenticate Google Drive"):
        token_file_path = st.session_state.token_file_path
        if token_file_path is not None:
            service = authenticate_drive(token_file_path, token_file_path, is_service_account=True)
            if service:
                service = update_state("service", service)

                st.success("Google Drive authenticated successfully!")
            else:
                st.error("Failed to authenticate Google Drive.")
        else:
            st.error("Please upload a valid token file.")

    # List files in Google Drive
    st.divider()
    st.subheader("Upload to Google Drive")

    # Choose file to upload from the downloaded file folder
    if st.button("Refresh File List"):
        list_all_files = refresh_file_list()
        st.success("File list refreshed!")
    
    selected_file = st.selectbox("Select a video file to upload:", list_all_files)
    
    # add folder id or select folder
    folder_id_input = st.text_input("Enter the Google Drive folder ID (optional):")
    if folder_id_input and folder_id_input.strip():
        folder_id_input = folder_id_input.strip()
    else:
        folder_id_input = None

    # Get list of folders in Google Drive
    def check_service():
        if st.session_state.service:
            service = st.session_state.service
        else:
            service = authenticate_drive("temp_credentials.json", "temp_credentials.json", is_service_account=True)
        
        return service

    service = check_service()

    if service:
        folders = get_lists_of_folders(service, "10514rVBAqv21ry4gvRK-EP2wAxq3cjU6")
        folder_names = [folder["name"] for folder in folders]
        folder_ids = [folder["id"] for folder in folders]
        selected_folder = st.selectbox("Select a folder to upload the file:", folder_names)
        if selected_folder:
            folder_id = folder_ids[folder_names.index(selected_folder)]
        else:
            folder_id = None
    else:
        st.error("Google Drive service not authenticated. Please authenticate first.")


    if folder_id:
        folder_id = folder_id.strip()
    else:
        folder_id = None

    if st.button("Upload File"):
        if selected_file:
            file_path = f"downloaded-files/{selected_file}"
            file_name = selected_file
            
            # Upload the file to Google Drive
            service = check_service()
            
            if service:
                if folder_id_input:
                    folder_id = folder_id_input.strip()
                    
                file_id = upload_file_to_drive(service, file_path, file_name, folder_id)
                if file_id:
                    st.success(f"File {selected_file} uploaded to Google Drive with ID: {file_id}")
                else:
                    st.error("Failed to upload the file.")
            else:
                st.error("Google Drive service not authenticated. Please authenticate first.")
        else:
            st.error("Please select a file to upload.")
  

if __name__ == "__main__":
    main()