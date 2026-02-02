const socket = io();

// Initial connection
socket.on('connect', () => {
    console.log('Connected to server via WebSocket');
});

socket.on('new_upload', (data) => {
    const liveFeed = document.getElementById('live-feed');
    if (liveFeed) {
        const item = document.createElement('div');
        item.style.cssText = 'background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px; animation: fadeIn 0.5s;';

        item.innerHTML = `
            <img src="${data.image_url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">
            <div>
                <p style="margin: 0; font-weight: bold; font-size: 0.9em;">${data.username}</p>
                <p style="margin: 0; font-size: 0.8em; color: #aaa;">Uploaded ${data.filename}</p>
            </div>
        `;

        liveFeed.insertBefore(item, liveFeed.firstChild);
    }
});

// DOM Elements
const uploadBtn = document.getElementById('uploadBtn');
const imageInput = document.getElementById('imageInput');
const resultsArea = document.getElementById('resultsArea');
const processedImage = document.getElementById('processedImage');
const jsonResults = document.getElementById('jsonResults');

uploadBtn.addEventListener('click', async () => {
    const file = imageInput.files[0];
    if (!file) {
        alert("Please select an image first.");
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data);

            // Show results area
            resultsArea.style.display = 'flex';

            // Set processed image
            processedImage.src = data.processed_image_url;

            // Format JSON results
            jsonResults.textContent = JSON.stringify(data, null, 2);

            // Render formatted results
            const formattedContainer = document.getElementById('formatted-results');
            formattedContainer.innerHTML = '';

            data.objects.forEach(obj => {
                const item = document.createElement('div');
                item.className = 'result-item';
                const confidencePct = (obj.confidence * 100).toFixed(1) + '%';

                item.innerHTML = `
                    <div>
                        <strong>${obj.name}</strong>
                        <div class="confidence-bar" style="width: ${confidencePct}"></div>
                    </div>
                    <span>${confidencePct} Accuracy</span>
                `;
                formattedContainer.appendChild(item);
            });

            // Render Extracted Items (Crops)
            const extractedArea = document.getElementById('extractedArea');
            const extractedGallery = document.getElementById('extractedGallery');
            extractedGallery.innerHTML = '';

            if (data.extracted_items_urls && data.extracted_items_urls.length > 0) {
                extractedArea.style.display = 'block';
                data.extracted_items_urls.forEach(imgUrl => {
                    const img = document.createElement('img');
                    img.src = imgUrl;
                    extractedGallery.appendChild(img);
                });
            } else {
                extractedArea.style.display = 'none';
            }

            // Render Related Images
            const relatedArea = document.getElementById('relatedArea');
            const relatedGallery = document.getElementById('relatedGallery');
            relatedGallery.innerHTML = '';

            if (data.related_images && data.related_images.length > 0) {
                relatedArea.style.display = 'block';
                data.related_images.forEach(imgUrl => {
                    const img = document.createElement('img');
                    img.src = imgUrl;
                    relatedGallery.appendChild(img);
                });
            } else {
                relatedArea.style.display = 'none';
            }

        } else {
            alert("Upload failed");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred");
    }
});
