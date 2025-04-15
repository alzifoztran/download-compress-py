# def download_from_url(url):
#     import yt_dlp

#     info_dict = ydl.extract_info(url, download=True)

#     # Extract the actual file name from the template
#     downloaded_file_name = info_dict['title'] + '.' + info_dict['ext']

#     return downloaded_file_name

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     output_filename = download_from_url(url)

#     print(output_filename)


def new_download(url):
    import yt_dlp

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "downloaded-files/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_name = ydl.prepare_filename(info_dict)

    return file_name


# For downloading non-video files like a zip file, use the `requests` library.
def download_file(
    url, output_dir="downloaded-files", progress_bar=None, progress_text=None
):
    import requests
    from pathlib import Path

    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an error for bad status codes

    # Extract the file name from the URL
    file_name = url.split("/")[-1]
    output_path = Path(output_dir) / file_name

    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file to the output directory
    progress_value = 0
    len_response = len(response.content)
    with open(output_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            progress_value += len(chunk) / len_response
            if progress_bar:
                progress_bar.progress(
                    progress_value,
                    text=f"Downloading {file_name}...  {progress_value:.2%}",
                )
            file.write(chunk)

    if progress_bar:
        progress_bar.progress(1.0, text=f"Download complete: {file_name}")

    return str(output_path)


def delete_file(file_path):
    import os

    try:
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
