document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const selectBtn = document.getElementById('selectBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileCount = document.getElementById('fileCount');
    const galleryGrid = document.getElementById('galleryGrid');
    const uploadStatus = document.getElementById('uploadStatus');

    // Load existing gallery
    loadGallery();

    selectBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        const count = fileInput.files.length;
        fileCount.textContent = count > 0 ? `${count} files selected` : 'No files selected';
        uploadBtn.disabled = count === 0;
    });

    uploadBtn.addEventListener('click', async () => {
        if (fileInput.files.length === 0) return;

        const formData = new FormData();
        for (let i = 0; i < fileInput.files.length; i++) {
            formData.append('files', fileInput.files[i]);
        }

        try {
            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Uploading...';
            uploadStatus.textContent = 'Uploading and processing images...';
            uploadStatus.classList.remove('hidden');

            const response = await fetch('/gallery/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            // Display results
            let successCount = 0;
            let errorCount = 0;

            data.results.forEach(res => {
                if (res.status === 'success') {
                    successCount++;
                } else {
                    errorCount++;
                    console.error(`Error uploading ${res.filename}: ${res.message}`);
                }
            });

            uploadStatus.textContent = `Upload complete. Success: ${successCount}, Errors: ${errorCount}`;

            // Refresh gallery
            loadGallery();

            // Reset input
            fileInput.value = '';
            fileCount.textContent = 'No files selected';

        } catch (error) {
            uploadStatus.textContent = `Upload failed: ${error.message}`;
            uploadStatus.className = 'error';
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload & Process';
        }
    });

    async function loadGallery() {
        try {
            const response = await fetch('/gallery/list');
            const data = await response.json();

            galleryGrid.innerHTML = '';
            data.images.forEach(img => {
                const div = document.createElement('div');
                div.className = 'gallery-item';
                div.innerHTML = `
                    <img src="${img.imageUrl}" alt="${img.filename}" loading="lazy">
                `;
                galleryGrid.appendChild(div);
            });
        } catch (error) {
            console.error('Error loading gallery:', error);
        }
    }
});
