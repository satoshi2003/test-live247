from flask import Flask, Response
import yt_dlp

app = Flask(__name__)

def get_live_info(channel_handle):
    """Hàm dùng yt-dlp để lấy thông tin livestream hiện tại"""
    live_url = f"https://www.youtube.com/{channel_handle}/live"
    
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'extract_flat': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Lấy thông tin video mà không tải xuống
            info = ydl.extract_info(live_url, download=False)
            
            title = info.get('title', '🔴 LIVE 24/7 | Live Stream')
            video_url = f"https://www.youtube.com/watch?v={info.get('id')}"
            
            return title, video_url
    except Exception as e:
        return None, None

@app.route('/playlist.m3u')
def generate_m3u():
    # Thay handle của kênh bạn muốn lấy ở đây
    channel_handle = "@PowerRangersOfficial" 
    
    title, video_url = get_live_info(channel_handle)
    
    if not video_url:
        return Response("Kênh hiện không có luồng trực tiếp hoặc có lỗi xảy ra.", status=404)

    # Tạo nội dung chuẩn M3U / IPTV theo yêu cầu của bạn
    m3u_content = f"""#EXTM3U
#EXTINF:-1 tvg-logo="" group-title="Youtube",{title}
{video_url}
"""
    
    # Trả về dưới dạng file playlist để các app IPTV có thể đọc được
    return Response(m3u_content, mimetype='application/vnd.apple.mpegurl')

# Mở rộng: Endpoint cho phép truyền tên kênh bất kỳ (Ví dụ: /live/@LofiGirl)
@app.route('/live/<handle>.m3u')
def generate_m3u_dynamic(handle):
    if not handle.startswith('@'):
        handle = f"@{handle}"
        
    title, video_url = get_live_info(handle)
    
    if not video_url:
        return Response(f"Kênh {handle} hiện không live.", status=404)

    m3u_content = f"""#EXTM3U\n#EXTINF:-1 tvg-logo="" group-title="Youtube",{title}\n{video_url}\n"""
    return Response(m3u_content, mimetype='application/vnd.apple.mpegurl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
