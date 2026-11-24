from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FBDown - Facebook Video Downloader (HD, Reels, Private & MP4)</title>
    <meta name="description" content="Download Facebook videos, Reels, Watch videos, and private videos in 1080p Full HD, 720p HD, and SD MP4 format for free.">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        html { scroll-behavior: smooth; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased">

    <!-- Navbar -->
    <nav class="bg-white/95 backdrop-blur border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <a href="#top" class="flex items-center gap-2.5 text-2xl font-extrabold text-blue-600">
                <i class="fa-brands fa-facebook text-3xl"></i>
                <span>FB<span class="text-slate-900">Down</span></span>
            </a>

            <div class="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-600">
                <a href="#how-to-use" class="hover:text-blue-600 transition">How to Use</a>
                <a href="#features" class="hover:text-blue-600 transition">Features</a>
                <a href="#faq" class="hover:text-blue-600 transition">FAQ</a>
                <a href="#disclaimer" class="hover:text-blue-600 transition">Disclaimer</a>
            </div>

            <span class="text-xs bg-blue-50 text-blue-700 border border-blue-200 font-semibold px-3 py-1.5 rounded-full">
                Free HD Downloader
            </span>
        </div>
    </nav>

    <!-- Hero & Downloader Section -->
    <section id="top" class="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-900 text-white pt-12 pb-16 px-4">
        <div class="max-w-4xl mx-auto text-center">
            <div class="inline-flex items-center gap-2 bg-white/10 border border-white/20 px-4 py-1.5 rounded-full text-xs font-medium mb-4">
                <i class="fa-solid fa-bolt text-amber-300"></i>
                <span>Fast, Free & No Watermark • Public & Private Videos</span>
            </div>

            <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight mb-3">
                Facebook Video Downloader
            </h1>
            <p class="text-blue-100 text-base sm:text-lg max-w-2xl mx-auto mb-8">
                Download Facebook Videos, Reels, and Watch clips in 1080p Full HD, 720p HD, or SD MP4 format directly to your phone or computer.
            </p>

            <!-- Mode Tabs -->
            <div class="inline-flex bg-blue-950/60 p-1.5 rounded-xl border border-white/15 mb-6">
                <button id="tabPublic" onclick="switchTab('public')"
                    class="px-5 py-2.5 rounded-lg text-sm font-bold bg-white text-blue-700 shadow transition cursor-pointer">
                    <i class="fa-solid fa-globe mr-1.5"></i> Public Video
                </button>
                <button id="tabPrivate" onclick="switchTab('private')"
                    class="px-5 py-2.5 rounded-lg text-sm font-bold text-blue-100 hover:text-white transition cursor-pointer">
                    <i class="fa-solid fa-lock mr-1.5"></i> Private Video
                </button>
            </div>

            <!-- PUBLIC VIDEO BOX -->
            <div id="publicBox" class="bg-white p-2.5 rounded-2xl shadow-2xl max-w-3xl mx-auto">
                <div class="flex flex-col sm:flex-row gap-2">
                    <div class="relative flex-1 flex items-center">
                        <input type="text" id="fbUrl" placeholder="Paste Facebook video, Reels, or fb.watch link here..."
                            class="w-full pl-4 pr-24 py-3.5 text-slate-800 rounded-xl focus:outline-none text-base">
                        <button onclick="pasteLink('fbUrl')" type="button"
                            class="absolute right-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-3 py-2 rounded-lg transition cursor-pointer">
                            <i class="fa-regular fa-clipboard mr-1"></i> Paste
                        </button>
                    </div>
                    <button onclick="fetchVideo()" id="downloadBtn" type="button"
                        class="bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-8 py-3.5 rounded-xl transition flex items-center justify-center gap-2 shadow-md cursor-pointer">
                        <i class="fa-solid fa-download"></i>
                        <span>Download</span>
                    </button>
                </div>
            </div>

            <!-- PRIVATE VIDEO BOX -->
            <div id="privateBox" class="hidden bg-white p-5 rounded-2xl shadow-2xl max-w-3xl mx-auto text-left text-slate-800">
                <div class="bg-amber-50 border border-amber-200 text-amber-900 text-xs sm:text-sm p-3.5 rounded-xl mb-3 leading-relaxed">
                    <strong>How to get Private Video Source:</strong> Open the private video on Facebook in a browser &rarr; add <code class="bg-amber-100 px-1.5 py-0.5 rounded font-mono">view-source:</code> before <code class="bg-amber-100 px-1.5 py-0.5 rounded font-mono">https://</code> &rarr; press <strong>Ctrl+A</strong> then <strong>Ctrl+C</strong> &rarr; paste the source code below.
                </div>
                <textarea id="privateSource" rows="5" placeholder="Paste Facebook video page source code (view-source:) here..."
                    class="w-full p-3.5 border border-slate-300 rounded-xl text-xs font-mono text-slate-700 focus:outline-none focus:border-blue-500 mb-3"></textarea>
                <div class="flex flex-wrap items-center justify-between gap-2">
                    <button onclick="pasteLink('privateSource')" type="button"
                        class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-4 py-2.5 rounded-lg transition cursor-pointer">
                        <i class="fa-regular fa-clipboard mr-1"></i> Paste Source Code
                    </button>
                    <button onclick="extractPrivateVideo()" type="button"
                        class="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2.5 rounded-xl text-sm transition flex items-center gap-2 cursor-pointer">
                        <i class="fa-solid fa-unlock-keyhole"></i> Extract Video Links
                    </button>
                </div>
            </div>

            <p id="errorMsg" class="text-amber-300 font-medium text-sm mt-4 hidden"></p>
        </div>
    </section>

    <!-- Loading Spinner -->
    <div id="loader" class="hidden max-w-2xl mx-auto mt-10 text-center px-4">
        <div class="inline-block animate-spin rounded-full h-11 w-11 border-4 border-blue-600 border-t-transparent"></div>
        <p class="mt-3 text-slate-600 font-semibold">Fetching video links from Facebook... Please wait.</p>
    </div>

    <!-- Video Result Section -->
    <section id="resultBox" class="hidden max-w-4xl mx-auto mt-8 px-4">
        <div class="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden p-6">
            <div class="flex flex-col sm:flex-row gap-5 items-center mb-6 pb-5 border-b border-slate-100">
                <img id="videoThumb" src="" alt="Thumbnail" class="w-full sm:w-52 h-32 object-cover rounded-xl bg-slate-200 shadow-sm">
                <div class="flex-1 text-center sm:text-left">
                    <span class="inline-block text-xs font-bold uppercase tracking-wider bg-blue-100 text-blue-700 px-2.5 py-1 rounded-md mb-2">Ready to Download</span>
                    <h2 id="videoTitle" class="font-bold text-lg sm:text-xl text-slate-800 line-clamp-2">Facebook Video</h2>
                    <p id="videoDuration" class="text-sm text-slate-500 mt-1"></p>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-100 text-slate-700 text-sm">
                            <th class="py-3 px-4 rounded-tl-xl">Quality</th>
                            <th class="py-3 px-4">Format</th>
                            <th class="py-3 px-4 text-right rounded-tr-xl">Download</th>
                        </tr>
                    </thead>
                    <tbody id="downloadLinks" class="divide-y divide-slate-200 text-sm">
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <!-- How to Use Section -->
    <section id="how-to-use" class="max-w-6xl mx-auto py-16 px-4">
        <div class="text-center max-w-2xl mx-auto mb-10">
            <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-2">How to Download Facebook Videos?</h2>
            <p class="text-slate-600 text-sm sm:text-base">Save your favorite Facebook videos and Reels in just three simple steps.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mb-4 font-extrabold text-xl">1</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">Copy the Video Link</h3>
                <p class="text-sm text-slate-600 leading-relaxed">Open Facebook app or website, find the video or Reel you want to save, tap <strong>Share</strong>, and select <strong>Copy Link</strong>.</p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mb-4 font-extrabold text-xl">2</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">Paste URL & Process</h3>
                <p class="text-sm text-slate-600 leading-relaxed">Paste the copied link into the search box above and click the green <strong>Download</strong> button to fetch available video qualities.</p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mb-4 font-extrabold text-xl">3</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">Save MP4 File</h3>
                <p class="text-sm text-slate-600 leading-relaxed">Choose your preferred quality (Full HD, HD, or SD) from the list and save the MP4 video directly to your device.</p>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="bg-white border-y border-slate-200 py-16 px-4">
        <div class="max-w-6xl mx-auto">
            <div class="text-center max-w-2xl mx-auto mb-10">
                <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-2">Why Use FBDown?</h2>
                <p class="text-slate-600 text-sm sm:text-base">Designed for speed, simplicity, and compatibility across all devices.</p>
            </div>

            <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="p-5 rounded-2xl bg-slate-50 border border-slate-200">
                    <i class="fa-solid fa-film text-2xl text-blue-600 mb-3"></i>
                    <h3 class="font-bold text-slate-900 mb-1.5">HD & SD Quality</h3>
                    <p class="text-xs sm:text-sm text-slate-600">Download videos in crisp HD or lightweight SD MP4 depending on your storage and data needs.</p>
                </div>
                <div class="p-5 rounded-2xl bg-slate-50 border border-slate-200">
                    <i class="fa-solid fa-mobile-screen-button text-2xl text-emerald-600 mb-3"></i>
                    <h3 class="font-bold text-slate-900 mb-1.5">All Devices Supported</h3>
                    <p class="text-xs sm:text-sm text-slate-600">Works smoothly on Android, iPhone/iPad, Windows, macOS, and all modern web browsers.</p>
                </div>
                <div class="p-5 rounded-2xl bg-slate-50 border border-slate-200">
                    <i class="fa-solid fa-shield-halved text-2xl text-indigo-600 mb-3"></i>
                    <h3 class="font-bold text-slate-900 mb-1.5">No Login Required</h3>
                    <p class="text-xs sm:text-sm text-slate-600">No registration, password, or extra software installation needed to download public videos.</p>
                </div>
                <div class="p-5 rounded-2xl bg-slate-50 border border-slate-200">
                    <i class="fa-solid fa-bolt text-2xl text-amber-500 mb-3"></i>
                    <h3 class="font-bold text-slate-900 mb-1.5">Fast & Free</h3>
                    <p class="text-xs sm:text-sm text-slate-600">Unlimited free downloads with quick link extraction for Facebook videos and Reels.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section id="faq" class="max-w-4xl mx-auto py-16 px-4">
        <h2 class="text-2xl sm:text-3xl font-extrabold text-center text-slate-900 mb-8">Frequently Asked Questions (FAQ)</h2>

        <div class="space-y-4">
            <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                <h3 class="font-bold text-slate-900 mb-1.5">1. Is FBDown completely free to use?</h3>
                <p class="text-sm text-slate-600 leading-relaxed">Yes, FBDown is 100% free to use. You can download public Facebook videos and Reels without paying any fee or creating an account.</p>
            </div>
            <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                <h3 class="font-bold text-slate-900 mb-1.5">2. Where are downloaded videos saved on my device?</h3>
                <p class="text-sm text-slate-600 leading-relaxed">Downloaded MP4 files are usually saved in your browser's default <strong>Downloads</strong> folder or your phone's Gallery/Files app.</p>
            </div>
            <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                <h3 class="font-bold text-slate-900 mb-1.5">3. Can I download Facebook Reels and Watch videos?</h3>
                <p class="text-sm text-slate-600 leading-relaxed">Yes! As long as the video or Reel is public and accessible, you can paste its URL and fetch available download links.</p>
            </div>
            <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                <h3 class="font-bold text-slate-900 mb-1.5">4. Why did a video fail to download?</h3>
                <p class="text-sm text-slate-600 leading-relaxed">A video may fail if it is set to private, restricted by region/age, removed by the creator, or if the link is incomplete. Try copying a fresh link from Facebook.</p>
            </div>
        </div>
    </section>

    <!-- Disclaimer & Information Section -->
    <section id="disclaimer" class="bg-slate-100 border-t border-slate-200 py-14 px-4">
        <div class="max-w-5xl mx-auto bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm">
            <div class="flex items-center gap-2.5 text-amber-600 font-extrabold text-xl mb-4">
                <i class="fa-solid fa-circle-exclamation"></i>
                <h2>Disclaimer & Important Information</h2>
            </div>

            <div class="space-y-4 text-sm text-slate-600 leading-relaxed">
                <p>
                    <strong>1. No Affiliation with Meta / Facebook:</strong> FBDown is an independent web utility tool and is not affiliated with, endorsed by, sponsored by, or connected to Facebook, Instagram, or Meta Platforms, Inc. All trademarks, logos, and brand names belong to their respective owners.
                </p>
                <p>
                    <strong>2. Copyright & Intellectual Property:</strong> Users are solely responsible for how they use downloaded content. Downloading copyrighted material, music, or videos without permission from the rightful owner or creator may violate copyright laws and platform terms of service. Please use this tool only for personal, fair-use, or authorized content.
                </p>
                <p>
                    <strong>3. Privacy & Data Handling:</strong> We do not host Facebook videos on our servers, nor do we require users to log in with their Facebook credentials. Links or page source code pasted into the tool are processed only to generate download options.
                </p>
                <p>
                    <strong>4. Availability & Accuracy:</strong> Because external platforms regularly update their web structure and security policies, availability of specific video qualities or formats may change without prior notice. Service uptime and performance are provided on an "as-is" and "as-available" basis.
                </p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-slate-900 text-slate-400 py-8 px-4 text-center text-sm">
        <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <p>© 2026 FBDown - Facebook Video Downloader. All rights reserved.</p>
            <div class="flex items-center gap-5">
                <a href="#how-to-use" class="hover:text-white transition">How to Use</a>
                <a href="#faq" class="hover:text-white transition">FAQ</a>
                <a href="#disclaimer" class="hover:text-white transition">Disclaimer</a>
            </div>
        </div>
    </footer>

    <script>
        function switchTab(mode) {
            const tabPublic = document.getElementById('tabPublic');
            const tabPrivate = document.getElementById('tabPrivate');
            const publicBox = document.getElementById('publicBox');
            const privateBox = document.getElementById('privateBox');
            const errorMsg = document.getElementById('errorMsg');

            errorMsg.classList.add('hidden');

            if (mode === 'public') {
                tabPublic.className = "px-5 py-2.5 rounded-lg text-sm font-bold bg-white text-blue-700 shadow transition cursor-pointer";
                tabPrivate.className = "px-5 py-2.5 rounded-lg text-sm font-bold text-blue-100 hover:text-white transition cursor-pointer";
                publicBox.classList.remove('hidden');
                privateBox.classList.add('hidden');
            } else {
                tabPrivate.className = "px-5 py-2.5 rounded-lg text-sm font-bold bg-white text-blue-700 shadow transition cursor-pointer";
                tabPublic.className = "px-5 py-2.5 rounded-lg text-sm font-bold text-blue-100 hover:text-white transition cursor-pointer";
                privateBox.classList.remove('hidden');
                publicBox.classList.add('hidden');
            }
        }

        async function pasteLink(inputId) {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById(inputId).value = text;
            } catch (err) {
                alert('Please paste manually using Ctrl+V (or long press on mobile).');
            }
        }

        function renderResult(data) {
            document.getElementById('videoTitle').textContent = data.title || 'Facebook Video';
            document.getElementById('videoThumb').src = data.thumbnail || 'https://via.placeholder.com/320x180?text=Facebook+Video';
            document.getElementById('videoDuration').textContent = data.duration ? `Duration: ${data.duration}` : '';

            const tbody = document.getElementById('downloadLinks');
            tbody.innerHTML = '';

            data.formats.forEach(item => {
                const row = `
                    <tr>
                        <td class="py-3.5 px-4 font-semibold text-slate-800">${item.quality}</td>
                        <td class="py-3.5 px-4 text-slate-600 uppercase">${item.ext}</td>
                        <td class="py-3.5 px-4 text-right">
                            <a href="${item.url}" target="_blank" rel="noopener noreferrer" download="fb_video.mp4"
                               class="inline-flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg transition">
                                <i class="fa-solid fa-download"></i> Download
                            </a>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });

            document.getElementById('resultBox').classList.remove('hidden');
            document.getElementById('resultBox').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        async function fetchVideo() {
            const url = document.getElementById('fbUrl').value.trim();
            const errorMsg = document.getElementById('errorMsg');
            const loader = document.getElementById('loader');
            const resultBox = document.getElementById('resultBox');
            const btn = document.getElementById('downloadBtn');

            errorMsg.classList.add('hidden');
            resultBox.classList.add('hidden');

            if (!url || (!url.includes('facebook.com') && !url.includes('fb.watch'))) {
                errorMsg.textContent = 'Please enter a valid Facebook video, Reels, or fb.watch link!';
                errorMsg.classList.remove('hidden');
                return;
            }

            loader.classList.remove('hidden');
            btn.disabled = true;

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });

                const data = await response.json();
                loader.classList.add('hidden');
                btn.disabled = false;

                if (data.error) {
                    errorMsg.textContent = data.error;
                    errorMsg.classList.remove('hidden');
                    return;
                }

                renderResult(data);
            } catch (err) {
                loader.classList.add('hidden');
                btn.disabled = false;
                errorMsg.textContent = 'Server error or timeout! If the free server was sleeping, please try again in a few seconds.';
                errorMsg.classList.remove('hidden');
            }
        }

        function extractPrivateVideo() {
            const source = document.getElementById('privateSource').value;
            const errorMsg = document.getElementById('errorMsg');
            const resultBox = document.getElementById('resultBox');

            errorMsg.classList.add('hidden');
            resultBox.classList.add('hidden');

            if (!source || source.trim().length < 50) {
                errorMsg.textContent = 'Please paste valid Facebook page source code first!';
                errorMsg.classList.remove('hidden');
                return;
            }

            const cleanSource = source.replace(/\\u0025/g, '%').replace(/\\\//g, '/');
            const patterns = [
                { label: 'HD Quality (MP4)', regex: /"browser_native_hd_url":"([^"]+)"/i },
                { label: 'SD Quality (MP4)', regex: /"browser_native_sd_url":"([^"]+)"/i },
                { label: 'HD Video URL', regex: /"hd_src":"([^"]+)"/i },
                { label: 'SD Video URL', regex: /"sd_src":"([^"]+)"/i },
                { label: 'Playable HD URL', regex: /"playable_url_quality_hd":"([^"]+)"/i },
                { label: 'Playable URL', regex: /"playable_url":"([^"]+)"/i }
            ];

            const foundFormats = [];
            const seenUrls = new Set();

            patterns.forEach(p => {
                const match = cleanSource.match(p.regex);
                if (match && match[1]) {
                    const finalUrl = match[1].replace(/\\u003C/g, '<').replace(/\\u003E/g, '>').replace(/&amp;/g, '&');
                    if (!seenUrls.has(finalUrl)) {
                        seenUrls.add(finalUrl);
                        foundFormats.push({
                            quality: p.label,
                            ext: 'mp4',
                            url: finalUrl
                        });
                    }
                }
            });

            if (foundFormats.length === 0) {
                errorMsg.textContent = 'Could not detect a direct video URL in the pasted source code. Make sure you copied the full page source of a video post.';
                errorMsg.classList.remove('hidden');
                return;
            }

            renderResult({
                title: 'Extracted Facebook Video',
                thumbnail: '',
                duration: '',
                formats: foundFormats
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/api/download', methods=['POST'])
def get_video():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats_list = []

            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    height = f.get('height')
                    quality_label = f"{height}p (HD)" if height and height >= 720 else (f"{height}p (SD)" if height else "Standard MP4")
                    formats_list.append({
                        'quality': quality_label,
                        'ext': f.get('ext', 'mp4'),
                        'url': f.get('url')
                    })

            if not formats_list and info.get('url'):
                formats_list.append({
                    'quality': 'Best Available MP4',
                    'ext': 'mp4',
                    'url': info.get('url')
                })

            seen = set()
            unique_formats = []
            for item in reversed(formats_list):
                if item['quality'] not in seen:
                    seen.add(item['quality'])
                    unique_formats.append(item)

            duration_sec = info.get('duration')
            duration_str = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}" if duration_sec else ""

            return jsonify({
                'title': info.get('title', 'Facebook Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': duration_str,
                'formats': unique_formats
            })

    except Exception:
        return jsonify({'error': 'Could not fetch video. Make sure the video is Public and the link is correct.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
