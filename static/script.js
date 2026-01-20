document.addEventListener('DOMContentLoaded', () => {

    let currentSegments = []; // Store for translation

    // --- URL Analysis ---
    const urlInput = document.querySelector('input[type="text"]');
    const analyzeBtn = document.querySelector('.btn-primary');

    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert("Iltimos, video URL manzilini kiriting!");
            return;
        }

        // UI update: Loading state
        const originalText = analyzeBtn.innerText;
        analyzeBtn.innerText = "Tahlil qilinmoqda...";
        analyzeBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('url', url);

            const response = await fetch('/api/analyze-url', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Show result and ask to proceed
                const proceed = confirm(`Video topildi: ${result.data.video_title}\nDavomiyligi: ${result.data.duration}\n\n"Dublyajlashni boshlash" tugmasini bosib audioni yuklab olish va tahlil qilishni boshlaysizmi?`);

                if (proceed) {
                    await startProcessing(url, result.data.video_title);
                }
            } else {
                alert("Xatolik yuz berdi.");
            }

        } catch (error) {
            console.error('Error:', error);
            alert("Serverga ulanishda xatolik.");
        } finally {
            analyzeBtn.innerText = originalText;
            analyzeBtn.disabled = false;
        }
    });

    async function startProcessing(url, title) {
        const analyzeBtn = document.querySelector('.btn-primary');
        const originalText = analyzeBtn.innerText;
        analyzeBtn.innerText = "Audio yuklanmoqda...";
        analyzeBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('url', url);
            formData.append('original_title', title);

            const response = await fetch('/api/process-video', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message + "\nKeyingi bosqich: " + result.data.next_action);
            } else {
                alert("Xatolik: " + result.message);
            }
        } catch (error) {
            alert("Server xatosi");
        } finally {
            analyzeBtn.innerText = originalText;
            analyzeBtn.disabled = false;
        }
    }


    // --- File Upload ---
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'video/mp4,video/webm,video/quicktime,video/x-msvideo';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', async (e) => {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            await uploadFile(file);
        }
    });

    // Drag & Drop effects
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
        uploadArea.style.background = 'rgba(34, 211, 238, 0.05)';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'var(--bg-card)';
    });

    uploadArea.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.background = 'var(--bg-card)';

        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            await uploadFile(file);
        }
    });

    async function uploadFile(file) {
        // Simple validation
        if (file.size > 100 * 1024 * 1024) { // 100MB
            alert("Fayl hajmi 100MB dan oshmasligi kerak!");
            return;
        }

        // UI Update
        const originalText = document.querySelector('.upload-text').innerText;
        document.querySelector('.upload-text').innerText = `Yuklanmoqda: ${file.name}...`;

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload-video', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Render the results on the page
                currentSegments = result.data.segments; // SAVE SEGMENTS
                renderTranscript(result.data.segments);
                alert("Muvaffaqiyatli! Matn ekranga chiqdi.\nEndi 'Tarjima qilish' tugmasini bosishingiz mumkin.");
            } else {
                alert("Yuklashda xatolik: " + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert("Server xatosi.");
        } finally {
            document.querySelector('.upload-text').innerText = originalText;
            fileInput.value = ''; // Reset input
        }
    }

    // --- Translation Handler ---
    const translateBtn = document.getElementById('translate-btn');
    if (translateBtn) {
        translateBtn.addEventListener('click', async () => {
            if (currentSegments.length === 0) {
                alert("Tarjima qilish uchun avval matn bo'lishi kerak!");
                return;
            }

            const originalText = translateBtn.innerText;
            translateBtn.innerText = "Tarjima qilinmoqda...";
            translateBtn.disabled = true;

            try {
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ segments: currentSegments })
                });

                const result = await response.json();

                if (response.ok) {
                    renderTranscript(result.data.segments, true); // Show original too
                    alert("Tarjima tayyor!");
                } else {
                    alert("Xatolik: " + result.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert("Tarjima serverida xatolik.");
            } finally {
                translateBtn.innerText = originalText;
                translateBtn.disabled = false;
            }
        });
    }

    function renderTranscript(segments, showOriginal = false) {
        const resultsSection = document.getElementById('results-section');
        const container = document.getElementById('transcript-container');

        container.innerHTML = ''; // Clear previous results
        resultsSection.style.display = 'block';

        segments.forEach(seg => {
            const div = document.createElement('div');
            div.style.padding = '10px';
            div.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            div.style.display = 'flex';
            div.style.gap = '15px';

            const timeStart = new Date(seg.start * 1000).toISOString().substr(14, 5);
            const timeEnd = new Date(seg.end * 1000).toISOString().substr(14, 5);

            div.innerHTML = `
                <div style="font-family: monospace; color: var(--primary); font-size: 0.9em; min-width: 100px;">
                    ${timeStart} - ${timeEnd}
                </div>
                <div style="color: var(--text-white); width: 100%;">
                    <div style="font-weight: 600; font-size: 1.1em; margin-bottom: 4px;">${seg.text}</div>
                    ${showOriginal && seg.original ? `<div style="color: var(--text-gray); font-size: 0.85em; font-style: italic;">${seg.original}</div>` : ''}
                </div>
            `;
            container.appendChild(div);
        });

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

});
