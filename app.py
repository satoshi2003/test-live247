from flask import Flask, Response
import requests
import re

app = Flask(__name__)

def get_live_url(channel_handle):
    """Mô phỏng trình duyệt để lấy link watch?v= trực tiếp từ HTML của YouTube"""
    url = f"https://www.youtube.com/{channel_handle}/live"
    
    # Giả mạo User-Agent để YouTube tưởng đây là người thật đang dùng Chrome
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Tìm thẻ canonical (chứa link video gốc) trong mã nguồn HTML
        match = re.search(r'<link rel="canonical" href="(https://www\.youtube\.com/watch\?v=([^"]+))">', response.text)
        
        if match:
            return match.group(1) # Trả về nguyên đoạn link: https://www.youtube.com/watch?v=...
        else:
            return "NOT_LIVE"
            
    except Exception as e:
        return f"ERROR: {str(e)}"

@app.route('/playlist.m3u')
def generate_m3u():
    channel_handle = "@PowerRangersOfficial" 
    
    result = get_live_url(channel_handle)
    
    # Xử lý các trường hợp lỗi để in ra màn hình cho dễ gỡ lỗi
    if result == "NOT_LIVE":
        return Response(f"Kênh {channel_handle} hiện không có luồng trực tiếp nào đang phát.", status=404, mimetype='text/plain; charset=utf-8')
    elif result.startswith("ERROR:"):
        return Response(f"Lỗi khi kết nối đến YouTube:\n{result}", status=500, mimetype='text/plain; charset=utf-8')

    # Nếu thành công, tạo định dạng M3U
    title = "🔴 LIVE 24/7 | Power Rangers Official"
    m3u_content = f"""#EXTM3U
#EXTINF:-1 tvg-logo="" group-title="Youtube",{title}
{result}
"""
    
    return Response(m3u_content, mimetype='application/vnd.apple.mpegurl')

# API mở rộng để test kênh khác (Ví dụ: /live/@SpaceX.m3u)
@app.route('/live/<handle>.m3u')
def generate_m3u_dynamic(handle):
    if not handle.startswith('@'):
        handle = f"@{handle}"
        
    result = get_live_url(handle)
    
    if result == "NOT_LIVE":
        return Response(f"Kênh {handle} hiện không live.", status=404, mimetype='text/plain; charset=utf-8')
    elif result.startswith("ERROR:"):
        return Response(result, status=500, mimetype='text/plain; charset=utf-8')

    m3u_content = f"""#EXTM3U\n#EXTINF:-1 tvg-logo="" group-title="Youtube",🔴 LIVE | {handle}\n{result}\n"""
    return Response(m3u_content, mimetype='application/vnd.apple.mpegurl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
