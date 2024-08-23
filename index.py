import flet as ft
import yt_dlp
import os

def main(page: ft.Page):
    page.title = "Video/Audio Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    url_input = ft.TextField(hint_text="Enter URL here", width=400)
    path_input = ft.TextField(hint_text="Choose download path", width=400, read_only=True)
    status_text = ft.Text()
    progress_bar = ft.ProgressBar(width=400, visible=False)
    download_speed = ft.Text()
    eta = ft.Text()

    def on_dialog_result(e: ft.FilePickerResultEvent):
        if e.path:
            path_input.value = e.path
            page.update()

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)

    def browse_click(e):
        file_picker.get_directory_path()

    browse_button = ft.ElevatedButton("Browse", on_click=browse_click)

    def download_progress_hook(d):
        if d['status'] == 'downloading':
            try:
                progress = float(d.get('_percent_str', '0%').replace('%', ''))
                speed = d.get('_speed_str', 'N/A')
                eta_str = d.get('_eta_str', 'N/A')
                
                progress_bar.value = progress / 100
                download_speed.value = f"Speed: {speed}"
                eta.value = f"ETA: {eta_str}"
                page.update()
            except ValueError:
                # If we can't parse the progress, just update the status
                status_text.value = "Downloading..."
                page.update()

    def download_with_format(format_option):
        url = url_input.value
        path = path_input.value

        if not url or not path:
            status_text.value = "Please enter a URL and choose a download path."
            page.update()
            return

        progress_bar.visible = True
        download_speed.visible = True
        eta.visible = True
        status_text.value = "Downloading..."
        page.update()

        try:
            if not os.path.exists(path):
                os.makedirs(path)

            ydl_opts = {
                'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
                'format': 'bestaudio/best' if format_option == 'audio' else 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'progress_hooks': [download_progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }] if format_option == 'video' else [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            status_text.value = f"Download complete. Saved to {path}"
        except Exception as e:
            status_text.value = f"An error occurred: {str(e)}"
        finally:
            progress_bar.visible = False
            download_speed.visible = False
            eta.visible = False
            page.update()

    def show_format_dialog(e):
        def close_dialog(e):
            format_dialog.open = False
            page.update()

        def format_selected(e, format_option):
            close_dialog(e)
            download_with_format(format_option)

        format_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Choose Download Format"),
            content=ft.Text("Do you want to download audio or video?"),
            actions=[
                ft.TextButton("Audio", on_click=lambda e: format_selected(e, 'audio')),
                ft.TextButton("Video (FHD)", on_click=lambda e: format_selected(e, 'video')),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = format_dialog
        format_dialog.open = True
        page.update()

    download_button = ft.ElevatedButton("Download", on_click=show_format_dialog)

    page.add(
        ft.Column(
            controls=[
                url_input,
                ft.Row([path_input, browse_button]),
                download_button,
                progress_bar,
                download_speed,
                eta,
                status_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

ft.app(target=main)