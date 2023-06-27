// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.innerHTML = `<h2>${post.title}</h2><p class="subtitle">Created by ${post.author} at ${post.date}</p><p>${post.content}</p>
                <div class="btns">
                <button class="delete-btn" onclick="deletePost(${post.id})">Delete</button>
                <button class="update-btn" onclick="openPopup(${post.id})">Update</button>
                </div>`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;

    // Generate today's date in "YYYY-MM-DD" format
    var currentDate = new Date();
    var year = currentDate.getFullYear();
    var month = String(currentDate.getMonth() + 1).padStart(2, '0');
    var day = String(currentDate.getDate()).padStart(2, '0');
    var postDate = year + '-' + month + '-' + day;

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent,
        author: postAuthor, date: postDate })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to show modal popup
function openPopup(postId) {
    var modal = document.getElementById('myModal');
    modal.style.display = 'block';

    // Sets the popup's form variables as empty and ID as the post ID
    var formId = document.getElementById('id');
    var formTitle = document.getElementById('title');
    var formContent = document.getElementById('content');
    var formAuthor = document.getElementById('author');
    var formDate = document.getElementById('date');
    formId.value = postId
    formTitle.value = '';
    formContent.value = '';
    formAuthor.value = '';
    formDate.value = '';

    var form = document.getElementById('updateForm');
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        var id = formId.value;
        var title = formTitle.value;
        var content = formContent.value;
        var author = formAuthor.value;
        var date = formDate.value;

        submitData(postId, title, content, author, date);
        closePopup();
    });
}

// Function to hide the modal popup
function closePopup() {
    var modal = document.getElementById('myModal');
    modal.style.display = 'none';
}

// Function to submit the PUT request to the API to update a post
function submitData(postId, title, content, author, date) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Construct the data object
    var data = { id: postId };

    if (title !== '') {data.title = title;}
    if (content !== '') {data.content = content;}
    if (author !== '') {data.author = author;}
    if (date !== '') {data.date = date;}

    // Send the data as JSON via PUT request
    fetch(baseUrl + '/posts/' + postId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log('Data submitted:', result);
        loadPosts(); // Reload all posts after updating
    })

    .catch(error => console.error('Error:', error));
}
