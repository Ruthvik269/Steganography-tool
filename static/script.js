document.addEventListener('DOMContentLoaded', () => {
    // Tabs
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // State
    let maxCapacity = 0;

    // File Upload Handling
    setupFileUpload('encode-dropzone', 'encode-file', 'encode-file-info', true);
    setupFileUpload('decode-dropzone', 'decode-file', 'decode-file-info', false);

    function setupFileUpload(dropzoneId, inputId, infoId, isEncode) {
        const dropzone = document.getElementById(dropzoneId);
        const input = document.getElementById(inputId);
        const info = document.getElementById(infoId);

        dropzone.addEventListener('click', () => input.click());

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0], info, isEncode);
            }
        });

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                handleFileSelect(e.dataTransfer.files[0], info, isEncode);
            }
        });
    }

    function handleFileSelect(file, infoElement, isEncode) {
        infoElement.textContent = `Selected: ${file.name}`;

        if (isEncode) {
            checkCapacity(file);
        }
    }

    async function checkCapacity(file) {
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('/api/capacity', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                maxCapacity = data.capacity;
                updateCapacityUI();
                document.getElementById('capacity-container').classList.remove('hidden');
            }
        } catch (err) {
            console.error("Failed to check capacity", err);
        }
    }

    // Capacity UI Update
    const textArea = document.getElementById('secret-message');
    const capacityText = document.getElementById('capacity-text');
    const capacityFill = document.getElementById('capacity-fill');

    textArea.addEventListener('input', updateCapacityUI);

    function updateCapacityUI() {
        if (maxCapacity === 0) return;

        const currentLength = textArea.value.length;
        capacityText.textContent = `${currentLength} / ${maxCapacity} chars`;

        const percentage = Math.min((currentLength / maxCapacity) * 100, 100);
        capacityFill.style.width = `${percentage}%`;

        if (percentage > 90) {
            capacityFill.style.backgroundColor = 'var(--danger)';
        } else if (percentage > 70) {
            capacityFill.style.backgroundColor = 'var(--warning)';
        } else {
            capacityFill.style.backgroundColor = 'var(--success)';
        }
    }

    // Encode Action
    const encodeBtn = document.getElementById('encode-btn');
    const encodeStatus = document.getElementById('encode-status');

    encodeBtn.addEventListener('click', async () => {
        const fileInput = document.getElementById('encode-file');
        const textInput = document.getElementById('secret-message');
        const passwordInput = document.getElementById('encode-password');

        if (!fileInput.files[0] || !textInput.value) {
            showStatus(encodeStatus, 'Please select an image and enter text.', 'error');
            return;
        }

        if (textInput.value.length > maxCapacity) {
            showStatus(encodeStatus, 'Message is too long for this image!', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        formData.append('text', textInput.value);
        if (passwordInput.value) {
            formData.append('password', passwordInput.value);
        }

        encodeBtn.textContent = 'Processing...';
        encodeBtn.disabled = true;

        try {
            const response = await fetch('/api/encode', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'encoded_image.png';
                document.body.appendChild(a);
                a.click();
                a.remove();

                showStatus(encodeStatus, 'Image encoded and downloaded!', 'success');
            } else {
                const data = await response.json();
                showStatus(encodeStatus, data.error || 'Encoding failed', 'error');
            }
        } catch (err) {
            showStatus(encodeStatus, 'An error occurred.', 'error');
        } finally {
            encodeBtn.textContent = 'Hide Message & Download';
            encodeBtn.disabled = false;
        }
    });

    // Decode Action
    const decodeBtn = document.getElementById('decode-btn');
    const decodeStatus = document.getElementById('decode-status');
    const resultBox = document.getElementById('decode-result-box');
    const decodedMessage = document.getElementById('decoded-message');

    decodeBtn.addEventListener('click', async () => {
        const fileInput = document.getElementById('decode-file');
        const passwordInput = document.getElementById('decode-password');

        if (!fileInput.files[0]) {
            showStatus(decodeStatus, 'Please select an image to decode.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        if (passwordInput.value) {
            formData.append('password', passwordInput.value);
        }

        decodeBtn.textContent = 'Decoding...';
        decodeBtn.disabled = true;
        resultBox.classList.add('hidden');

        try {
            const response = await fetch('/api/decode', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                decodedMessage.textContent = data.text;
                resultBox.classList.remove('hidden');
                showStatus(decodeStatus, 'Message revealed successfully!', 'success');
            } else {
                showStatus(decodeStatus, data.error || 'Decoding failed', 'error');
            }
        } catch (err) {
            showStatus(decodeStatus, 'An error occurred.', 'error');
        } finally {
            decodeBtn.textContent = 'Reveal Message';
            decodeBtn.disabled = false;
        }
    });

    function showStatus(element, message, type) {
        element.textContent = message;
        element.className = `status-msg ${type}`;
        setTimeout(() => {
            element.textContent = '';
            element.className = 'status-msg';
        }, 5000);
    }
});
