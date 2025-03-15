document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    let videoFile = document.getElementById('videoInput').files[0];
    let tags = document.getElementById('tagsInput').value;

    let formData = new FormData();
    formData.append('video', videoFile);
    formData.append('tags', tags);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('videoInput').value = '';
        document.getElementById('tagsInput').value = '';
    })
    .catch(error => console.error('Ошибка:', error));
});

function searchVideos() {
    let tag = document.getElementById('searchInput').value;

    fetch('/search?tag=' + encodeURIComponent(tag))
    .then(response => response.json())
    .then(data => {
        let videoList = document.getElementById('videoList');
        videoList.innerHTML = '';

        data.videos.forEach(video => {
            let li = document.createElement('li');

            let videoElement = document.createElement('video');
            videoElement.src = window.location.origin + '/uploads/' + video;
            videoElement.controls = true;
            videoElement.width = 300;

            let deleteButton = document.createElement('button');
            deleteButton.innerText = '🗑 Удалить';
            deleteButton.classList.add('delete-btn');
            deleteButton.onclick = function () {
                deleteVideo(video, li);
            };

            li.appendChild(videoElement);
            li.appendChild(deleteButton);
            videoList.appendChild(li);
        });
    })
    .catch(error => console.error('Ошибка:', error));
}

function deleteVideo(filename, listItem) {
    fetch('/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (!data.error) {
            listItem.style.transition = 'opacity 0.5s';
            listItem.style.opacity = '0';
            setTimeout(() => listItem.remove(), 500);
        }
    })
    .catch(error => console.error('Ошибка:', error));
}
