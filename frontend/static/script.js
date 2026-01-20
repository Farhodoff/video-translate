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

    // Helper: Parse duration string (MM:SS or HH:MM:SS) to seconds
    function parseDuration(durationStr) {
        if (!durationStr) return 0;
        const parts = durationStr.split(':').map(Number);
        let seconds = 0;
        if (parts.length === 3) {
            seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
        } else if (parts.length === 2) {
            seconds = parts[0] * 60 + parts[1];
        } else {
            seconds = parts[0];
        }
        return seconds;
    }

    // Timer Interval Reference
    let countdownInterval;

    function startCountdown(durationSec, btn, originalText) {
        // M1 Pro Whisper Speed Factor approx 0.25 (4x faster than realtime) plus overhead
        let remaining = Math.ceil(durationSec * 0.25) + 5; // +5 sec buffer

        // Clear any existing
        if (countdownInterval) clearInterval(countdownInterval);

        function updateDisplay() {
            if (remaining <= 0) {
                btn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> So'nggi ishlovlar...`;
                return;
            }

            const m = Math.floor(remaining / 60);
            const s = remaining % 60;
            const timeStr = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;

            btn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Qolgan vaqt: <span style="font-family:monospace; font-weight:700;">${timeStr}</span>`;
            remaining--;
        }

        updateDisplay();
        countdownInterval = setInterval(updateDisplay, 1000);
    }

    // ==========================================
    // LANDING PAGE LOGIC
    // ==========================================
    function initLandingPage() {
        console.log("Landing Page Initialized");

        // --- 1. URL Analysis (Dublyaj Button) ---
        analyzeBtn.addEventListener('click', async (e) => {
            e.preventDefault();

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
                    const durationSec = parseDuration(result.data.duration);

                    const proceed = confirm(`Video topildi: ${result.data.video_title}\nDavomiyligi: ${result.data.duration}\n\nJarayonni boshlaysizmi?`);

                    if (proceed) {
                        await startProcessing(url, result.data.video_title, analyzeBtn, originalText, durationSec);
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
        async function startProcessing(url, title, btn, originalText, durationSec) {
            startCountdown(durationSec, btn, originalText);
            try {
                const formData = new FormData();
                formData.append('url', url);
                formData.append('original_title', title);

                const response = await fetch('/api/process-video', { method: 'POST', body: formData });
                const result = await response.json();

                if (response.ok) {
                    clearInterval(countdownInterval);
                    const pathParts = result.data.audio_path.split('/');
                    const fullFilename = pathParts[pathParts.length - 1];
                    const filename = fullFilename.substring(0, fullFilename.lastIndexOf('.')) || fullFilename;

                    window.location.href = `/dashboard?project=${filename}`;
                } else {
                    clearInterval(countdownInterval);
                    alert("Xatolik: " + result.message);
                    btn.innerText = originalText;
                    btn.disabled = false;
                }
            } catch (error) {
                clearInterval(countdownInterval);
                alert("Server xatosi: " + error.message);
                btn.innerText = originalText;
                btn.disabled = false;
            }
        }

        // --- 3. File Upload ---
        if (uploadBtn) {
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
            if (file.size > 100 * 1024 * 1024) {
                alert("Fayl hajmi 100MB dan oshmasligi kerak!");
                return;
            }

            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Tayyorlanmoqda...`;
            btn.style.pointerEvents = 'none';

            // Get Duration locally
            const videoElement = document.createElement('video');
            videoElement.preload = 'metadata';
            videoElement.src = URL.createObjectURL(file);

            videoElement.onloadedmetadata = async function () {
                window.URL.revokeObjectURL(videoElement.src);
                const duration = videoElement.duration;

                // Start Timer
                startCountdown(duration, btn, originalHTML);

                // Proceed with upload
                try {
                    const formData = new FormData();
                    formData.append('file', file);

                    const response = await fetch('/api/upload-video', { method: 'POST', body: formData });
                    const result = await response.json();

                    if (response.ok) {
                        clearInterval(countdownInterval); // Stop
                        const name = file.name;
                        const filename = name.substring(0, name.lastIndexOf('.')) || name;
                        window.location.href = `/dashboard?project=${filename}`;
                    } else {
                        clearInterval(countdownInterval);
                        alert("Yuklashda xatolik: " + result.message);
                        btn.innerHTML = originalHTML;
                        btn.style.pointerEvents = 'auto';
                    }
                } catch (error) {
                    clearInterval(countdownInterval);
                    console.error('Error:', error);
                    alert("Server xatosi.");
                    btn.innerHTML = originalHTML;
                    btn.style.pointerEvents = 'auto';
                }
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
        const saveBtn = document.getElementById('save-btn'); // NEW
        const deleteBtn = document.getElementById('delete-btn'); // NEW

        // Audio Settings
        const voiceSelect = document.getElementById('voice-select');
        const rateRange = document.getElementById('rate-range');
        const rateValue = document.getElementById('rate-value');
        const pitchRange = document.getElementById('pitch-range');
        const pitchValue = document.getElementById('pitch-value');

        // Init Sliders
        if (rateRange && rateValue) {
            rateRange.addEventListener('input', () => { rateValue.innerText = (rateRange.value >= 0 ? '+' : '') + rateRange.value + '%'; });
        }
        if (pitchRange && pitchValue) {
            pitchRange.addEventListener('input', () => { pitchValue.innerText = (pitchRange.value >= 0 ? '+' : '') + pitchRange.value + 'Hz'; });
        }

        let currentSegments = [];

        if (!projectId) {
            transcriptBody.innerHTML = '<div style="padding:20px; text-align:center;">Loyiha tanlanmagan.</div>';
            return;
        }

        // Set Title
        if (projectTitleElement) projectTitleElement.innerText = projectId;

        // Load Data
        fetchProjectData(projectId);

        // --- Save Project Logic ---
        if (saveBtn) {
            saveBtn.addEventListener('click', async () => {
                const originalHTML = saveBtn.innerHTML;
                saveBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i>';
                saveBtn.disabled = true;

                try {
                    const response = await fetch(`/api/project/${projectId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ segments: currentSegments })
                    });

                    if (response.ok) {
                        saveBtn.innerHTML = '<i class="ph ph-check"></i>';
                        setTimeout(() => { saveBtn.innerHTML = '<i class="ph ph-floppy-disk"></i>'; saveBtn.disabled = false; }, 2000);
                    } else {
                        alert("Saqlashda xatolik.");
                        saveBtn.innerHTML = originalHTML;
                        saveBtn.disabled = false;
                    }
                } catch (e) {
                    alert("Server xatosi");
                    saveBtn.innerHTML = originalHTML;
                    saveBtn.disabled = false;
                }
            });
        }

        // --- Delete Project Logic ---
        if (deleteBtn) {
            deleteBtn.addEventListener('click', async () => {
                if (!confirm("Haqiqatan ham bu loyihani o'chirib tashlamoqchimisiz? Bu amalni qaytarib bo'lmaydi.")) return;

                const originalHTML = deleteBtn.innerHTML;
                deleteBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i>';
                deleteBtn.disabled = true;

                try {
                    const response = await fetch(`/api/project/${projectId}`, { method: 'DELETE' });

                    if (response.ok) {
                        alert("Loyiha o'chirildi!");
                        window.location.href = "/";
                    } else {
                        alert("O'chirishda xatolik.");
                        deleteBtn.innerHTML = originalHTML;
                        deleteBtn.disabled = false;
                    }
                } catch (e) {
                    alert("Server xatosi");
                    deleteBtn.innerHTML = originalHTML;
                    deleteBtn.disabled = false;
                }
            });
        }

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

            segments.forEach((seg, index) => {
                const div = document.createElement('div');
                div.className = 'segment-row';

                const timeStart = new Date(seg.start * 1000).toISOString().substr(14, 5);

                // Added contenteditable="true" and listeners
                div.innerHTML = `
                    <div class="time-col">${timeStart}</div>
                    <div class="text-original">${seg.text}</div>
                    <div class="text-translated" contenteditable="true" style="outline:none; transition: border-bottom 0.2s;">
                        ${seg.translated || ''} 
                    </div>
                     ${seg.translated ? `<button class="btn-play-audio" contenteditable="false" style="background:none; border:none; color:var(--primary); cursor:pointer; margin-left:8px;" title="Tinglash"><i class="ph-fill ph-speaker-high"></i></button>` : ''}
                `;

                const editable = div.querySelector('.text-translated');

                // Focus: Highlight
                editable.addEventListener('focus', () => {
                    editable.style.borderBottom = '1px solid var(--primary)';
                    div.classList.add('editing'); // custom class to avoid click conflicts
                });

                // Blur: Save to local state
                editable.addEventListener('blur', () => {
                    editable.style.borderBottom = 'none';
                    div.classList.remove('editing');
                    currentSegments[index].translated = editable.innerText.trim();
                });

                // Click to jump video (ignore if editing or clicking button)
                div.addEventListener('click', (e) => {
                    if (e.target.closest('.btn-play-audio') || e.target.closest('[contenteditable="true"]')) return;

                    videoPlayer.currentTime = seg.start;
                    videoPlayer.play();

                    // Highlight active row
                    document.querySelectorAll('.segment-row').forEach(r => r.classList.remove('active'));
                    div.classList.add('active');
                });

                // Play Audio Handler
                const playBtn = div.querySelector('.btn-play-audio');
                if (playBtn) {
                    playBtn.addEventListener('click', async () => {
                        const icon = playBtn.querySelector('i');
                        const originalIconClass = icon.className;

                        icon.className = 'ph ph-spinner ph-spin'; // Loading state
                        playBtn.disabled = true;

                        try {
                            // Gather Settings
                            const voice = voiceSelect ? voiceSelect.value : "uz-UZ-MadinaNeural";
                            const rate = rateValue ? rateValue.innerText : "+0%";
                            const pitch = pitchValue ? pitchValue.innerText : "+0Hz";

                            const formData = new FormData();
                            formData.append('text', currentSegments[index].translated);
                            formData.append('voice', voice);
                            formData.append('rate', rate);
                            formData.append('pitch', pitch);

                            const response = await fetch('/api/generate-audio', {
                                method: 'POST',
                                body: formData
                            });
                            const result = await response.json();

                            if (response.ok) {
                                const audio = new Audio(result.audio_url);
                                audio.play();

                                audio.onended = () => {
                                    icon.className = originalIconClass;
                                    playBtn.disabled = false;
                                };
                            } else {
                                alert("Ovoz generatsiya qilishda xatolik: " + result.message);
                                icon.className = originalIconClass;
                                playBtn.disabled = false;
                            }
                        } catch (error) {
                            console.error(error);
                            icon.className = originalIconClass;
                            playBtn.disabled = false;
                        }
                    });
                }

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
