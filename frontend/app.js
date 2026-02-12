document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('preview');
    const submitBtn = document.getElementById('submit-btn');
    const clearBtn = document.getElementById('clear-btn');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const errorMessageEl = document.getElementById('error-message');
    const loadingDiv = document.getElementById('loading');
    const mainCharsContainer = document.getElementById('main-plate-chars');
    const lastTwoContainer = document.getElementById('last-two-chars');
    const charCountEl = document.getElementById('char-count');
    const confidenceEl = document.getElementById('confidence');
    let selectedFile = null;

    // Click to upload
    dropArea.addEventListener('click', () => fileInput.click());

    // File change handler
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    // Drag and drop handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('drag-over'), false);
    });

    dropArea.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
            showError('فقط فرمت‌های JPG و PNG پشتیبانی می‌شوند');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);

        selectedFile = file;
        submitBtn.disabled = false;
        resultDiv.style.display = 'none';
        errorDiv.style.display = 'none';
        dropArea.style.display = 'none';
        clearBtn.style.display = 'none';
    }

    // Submit button handler
    submitBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        loadingDiv.style.display = 'block';
        submitBtn.disabled = true;
        errorDiv.style.display = 'none';

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://localhost:8000/recognize', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                charCountEl.textContent = result.character_count;
                confidenceEl.textContent = (result.confidence * 100).toFixed(1);
                displayPlate(result.characters);
                resultDiv.style.display = 'block';
                clearBtn.style.display = 'block';
            } else {
                showError(`خطا: ${result.status.replace('_', ' ')}`);
            }
        } catch (error) {
            showError('اتصال به سرور برقرار نشد. آیا سرور در حال اجراست؟');
        } finally {
            loadingDiv.style.display = 'none';
            submitBtn.disabled = false;
        }
    });

    // Display plate characters
    function displayPlate(chars) {
        // حذف محتوای قبلی
        mainCharsContainer.innerHTML = '';
        lastTwoContainer.innerHTML = '';

        // تبدیل به متن
        const plateText = chars.map(char => char.char).join('');

        // جداسازی دو رقم اخر
        const mainPart = plateText.slice(0, -2);
        const lastTwo = plateText.slice(-2);

        // نمایش بخش اصلی پلاک
        mainPart.split('').reverse().forEach(char => {
            const charSpan = document.createElement('span');
            charSpan.className = 'plate-char';
            charSpan.textContent = char;
            mainCharsContainer.appendChild(charSpan);
        });

        // نمایش دو رقم اخر زیر "ایران"
        lastTwo.split('').forEach(char => {
            const charSpan = document.createElement('span');
            charSpan.className = 'plate-char';
            charSpan.textContent = char;
            lastTwoContainer.appendChild(charSpan);
        });
    }

    // Clear button handler
    clearBtn.addEventListener('click', () => {
        selectedFile = null;
        preview.style.display = 'none';
        resultDiv.style.display = 'none';
        errorDiv.style.display = 'none';
        clearBtn.style.display = 'none';
        submitBtn.disabled = true;
        dropArea.style.display = 'block';
        fileInput.value = '';
        mainCharsContainer.innerHTML = '';
        lastTwoContainer.innerHTML = '';
        charCountEl.textContent = '';
        confidenceEl.textContent = '';
    });

    // Show error message
    function showError(message) {
        errorMessageEl.textContent = message;
        errorDiv.style.display = 'block';
        resultDiv.style.display = 'none';
        clearBtn.style.display = 'none';
    }
});
