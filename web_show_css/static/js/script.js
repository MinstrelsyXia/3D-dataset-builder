// script.js
document.getElementById('yes-button').addEventListener('click', () => {
    saveSelection('yes');
}, { once: true });

document.getElementById('unclear-button').addEventListener('click', () => {
    saveSelection('unclear');
}, { once: true });

document.getElementById('no-button').addEventListener('click', () => {
    saveSelection('no');
}, { once: true });

const modelViewer = document.getElementById('modelblock');
const descriptionElement = document.getElementById('description');
const buttons = document.querySelectorAll('.buttons button');

// Array to store model name and user selection
let modelData = [];

// Function to update the model-viewer src attribute
function updateModel(modelName, description) {
    modelViewer.src = modelName;  // Update src dynamically
    descriptionElement.textContent = description;  // Update description
}

// Function to save model name and selected option
function saveSelection(option) {
    const currentModel = modelViewer.src.split('/').pop();  // Get current model file name
    modelData.push({ model: currentModel, option: option });

    // Send data to server
    fetch('/save_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model: currentModel, response: option })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data saved successfully:', data);
        // Load next model
        fetch('/next-model')
            .then(response => response.json())
            .then(data => {
                if (data.src) {
                    updateModel(data.src, data.description);
                } else {
                    console.error('Error fetching next model:', data.error);
                }
            })
            .catch(error => console.error('Error fetching next model:', error));
    })
    .catch(error => console.error('Error saving data:', error));
}

// Event listeners for buttons
buttons.forEach(button => {
    button.addEventListener('click', () => {
        const option = button.getAttribute('data-option');
        saveSelection(option);
    });  // 确保每个按钮只绑定一次事件监听器
});

