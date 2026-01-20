document.addEventListener('DOMContentLoaded', () => {

    const currentPath = window.location.pathname;

    // Selectors
    // Landing Page Elements
    const urlInput = document.querySelector('.url-input-container input[type="text"]');
    const analyzeBtn = document.querySelector('.url-input-container .btn-primary'); // "Dublyaj" button
    const uploadBtn = document.querySelector('.upload-btn-full'); // "Video faylni yuklash"

    // Dashboard Elements
    const videoPlayer = document.getElementById('main-video');
    const transcriptBody = document.getElementById('transcript-body');
    const translateBtn = document.getElementById('translate-btn');

    // ==========================================
    // ROUTING LOGIC
    // ==========================================
    // Check if we are on Landing Page (Inputs exist) or Dashboard (Player exists)
    if (analyzeBtn && urlInput) {
        initLandingPage();
    }

    if (videoPlayer && transcriptBody) {
        initDashboardPage();
    }

    // ==========================================
    // LANDING PAGE LOGIC
    // ==========================================
    function initLandingPage() {
        console.log("Landing Page Initialized");

        // --- 1. URL Analysis (Dublyaj Button) ---
        analyzeBtn.addEventListener('click', async (e) => {
            e.preventDefault(); // Prevent accidental form submit if any

            const url = urlInput.value.trim();
            if (!url) {
                alert("Iltimos, video URL manzilini kiriting!");
                return;
            }

            // UI update
            const originalText = analyzeBtn.innerText;
            analyzeBtn.innerText = "Tahlil qilinmoqda...";
            analyzeBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('url', url);

                const response = await fetch('/api/analyze-url', { method: 'POST', body: formData });
                const result = await response.json();

                if (response.ok) {
                    const proceed = confirm(`Video topildi: ${result.data.video_title}\nDavomiyligi: ${result.data.duration}\n\n"Dublyajlash" tugmasini bosib davom ettirasizmi?`);
                    if (proceed) {
                        await startProcessing(url, result.data.video_title, analyzeBtn, originalText);
                    } else {
                        analyzeBtn.innerText = originalText;
                        analyzeBtn.disabled = false;
                    }
                } else {
                    alert("Xatolik: " + result.message);
                    analyzeBtn.innerText = originalText;
                    analyzeBtn.disabled = false;
                }

            } catch (error) {
                console.error('Error:', error);
                alert("Serverga ulanishda xatolik.");
                analyzeBtn.innerText = originalText;
                analyzeBtn.disabled = false;
            }
        });

        // --- 2. URL Processing Action ---
        async function startProcessing(url, title, btn, originalText) {
            btn.innerText = "Yuklanmoqda... (Biroz kuting)";
            try {
                const formData = new FormData();
                formData.append('url', url);
                formData.append('original_title', title);

                const response = await fetch('/api/process-video', { method: 'POST', body: formData });
                const result = await response.json();

                if (response.ok) {
                    // Extract safe filename for ID
                    const pathParts = result.data.audio_path.split('/');
                    const fullFilename = pathParts[pathParts.length - 1];
                    const filename = fullFilename.substring(0, fullFilename.lastIndexOf('.')) || fullFilename;

                    window.location.href = `/dashboard?project=${filename}`;
                } else {
                    alert("Xatolik: " + result.message);
                    btn.innerText = originalText;
                    btn.disabled = false;
                }
            } catch (error) {
                alert("Server xatosi: " + error.message);
                btn.innerText = originalText;
                btn.disabled = false;
            }
        }

        // --- 3. File Upload ---
        if (uploadBtn) {
            // Create hidden input dynamically
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'video/mp4,video/webm,video/quicktime,video/x-msvideo';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);

            uploadBtn.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', async () => {
                if (fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    await uploadFile(file, uploadBtn);
                }
            });
        }

        async function uploadFile(file, btn) {
            if (file.size > 100 * 1024 * 1024) { // 100MB
                alert("Fayl hajmi 100MB dan oshmasligi kerak!");
                return;
            }

            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Yuklanmoqda...`;
            btn.style.pointerEvents = 'none';

            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/upload-video', { method: 'POST', body: formData });
                const result = await response.json();

                if (response.ok) {
                    const name = file.name;
                    const filename = name.substring(0, name.lastIndexOf('.')) || name;
                    window.location.href = `/dashboard?project=${filename}`;
                } else {
                    alert("Yuklashda xatolik: " + result.message);
                    btn.innerHTML = originalHTML;
                    btn.style.pointerEvents = 'auto';
                }
            } catch (error) {
                console.error('Error:', error);
                alert("Server xatosi.");
                btn.innerHTML = originalHTML;
                btn.style.pointerEvents = 'auto';
            }
        }
    }

    // ==========================================
    // DASHBOARD PAGE LOGIC
    // ==========================================
    function initDashboardPage() {
        console.log("Dashboard Page Initialized");
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get('project');
        const projectTitleElement = document.querySelector('.breadcrumbs span');

        let currentSegments = [];

        if (!projectId) {
            transcriptBody.innerHTML = '<div style="padding:20px; text-align:center;">Loyiha tanlanmagan.</div>';
            return;
        }

        // Set Title
        if (projectTitleElement) projectTitleElement.innerText = projectId;

        // Load Data
        fetchProjectData(projectId);

        async function fetchProjectData(id) {
            try {
                const response = await fetch(`/api/project/${id}`);
                const result = await response.json();

                if (response.ok) {
                    const data = result.data;

                    // 1. Setup Video
                    videoPlayer.src = data.video_url;

                    // 2. Setup Transcript
                    currentSegments = data.segments;
                    renderTranscript(currentSegments);

                } else {
                    transcriptBody.innerHTML = `<div style="padding:20px; color:red;">Xatolik: ${result.message}</div>`;
                }
            } catch (error) {
                console.error("Fetch error:", error);
            }
        }

        function renderTranscript(segments) {
            transcriptBody.innerHTML = '';

            if (!segments || segments.length === 0) {
                transcriptBody.innerHTML = '<div style="padding:20px;">Matn topilmadi.</div>';
                return;
            }

            segments.forEach(seg => {
                const div = document.createElement('div');
                div.className = 'segment-row';

                const timeStart = new Date(seg.start * 1000).toISOString().substr(14, 5);

                div.innerHTML = `
                    <div class="time-col">${timeStart}</div>
                    <div class="text-original">${seg.text}</div>
                    <div class="text-translated">${seg.translated || '<i style="color:#666;">(Tarjima yo\'q)</i>'}</div>
                `;

                // Click to jump video
                div.addEventListener('click', () => {
                    videoPlayer.currentTime = seg.start;
                    videoPlayer.play();

                    // Highlight active row
                    document.querySelectorAll('.segment-row').forEach(r => r.classList.remove('active'));
                    div.classList.add('active');
                });

                transcriptBody.appendChild(div);
            });
        }

        // --- Translation Handler ---
        if (translateBtn) {
            translateBtn.addEventListener('click', async () => {
                if (currentSegments.length === 0) {
                    alert("Tarjima qilish uchun matn yo'q.");
                    return;
                }

                const originalHTML = translateBtn.innerHTML;
                translateBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Tarjima...`;
                translateBtn.disabled = true;

                try {
                    const response = await fetch('/api/translate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ segments: currentSegments })
                    });
                    const result = await response.json();

                    if (response.ok) {
                        // Merge translations back into currentSegments
                        const translatedSegs = result.data.segments;

                        // Mapping back
                        currentSegments = currentSegments.map((seg, idx) => {
                            if (translatedSegs[idx]) {
                                return { ...seg, translated: translatedSegs[idx].text };
                            }
                            return seg;
                        });

                        renderTranscript(currentSegments);
                        alert("Tarjima yakunlandi!");
                    } else {
                        alert("Xatolik: " + result.message);
                    }
                } catch (e) {
                    alert("Server xatosi");
                } finally {
                    translateBtn.innerHTML = originalHTML;
                    translateBtn.disabled = false;
                }
            });
        }
    }

});
