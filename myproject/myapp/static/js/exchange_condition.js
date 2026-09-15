// Photo preview function
function previewPhotos(event) {
    console.log('previewPhotos called');
    const input = event.target;
    const files = Array.from(input.files);
    const preview = document.getElementById("photo-preview");
    
    console.log('Files selected:', files.length);
    preview.innerHTML = "";
    
    if (files.length === 0) {
        console.log('No files selected');
        return;
    }
    
    // Warn if less than 2 photos
    if (files.length < 2) {
        console.warn("Please select at least 2 photos for submission.");
    }
    
    // Reject if more than 6 photos
    if (files.length > 6) {
        alert("Maximum 6 photos allowed. Please select fewer files.");
        input.value = "";
        preview.innerHTML = "";
        return;
    }
    
    let validCount = 0;
    files.forEach((file, index) => {
        console.log('Processing file:', file.name, file.type, file.size);
        
        // Validate file type
        if (file.type !== "image/jpeg" && file.type !== "image/png" && file.type !== "image/jpg") {
            alert(file.name + " is not a valid image. Use JPEG or PNG.");
            return;
        }
        
        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            alert(file.name + " is larger than 10MB.");
            return;
        }
        
        validCount++;
        
        // Display preview
        const reader = new FileReader();
        reader.onload = function (e) {
            const div = document.createElement("div");
            div.className = "relative rounded-lg overflow-hidden border border-outline-variant bg-surface-container-lowest aspect-[3/4]";
            div.innerHTML = `
                <img src="${e.target.result}" class="w-full h-full object-cover" alt="Selected photo ${validCount}">
                <div class="absolute top-3 left-3 bg-primary-container text-white px-2 py-1 rounded text-xs font-bold">#${validCount}</div>
            `;
            preview.appendChild(div);
            console.log('Preview added for photo:', validCount);
        };
        reader.readAsDataURL(file);
    });
    console.log('Total valid photos:', validCount);
}

// Initialize drag-and-drop and form validation
document.addEventListener("DOMContentLoaded", function() {
    console.log('DOMContentLoaded event fired');
    
    const fileInput = document.getElementById('photo-upload-input');
    const uploadLabel = document.querySelector('label[for="photo-upload-input"]');
    const form = document.querySelector('form');
    
    console.log('fileInput:', fileInput);
    console.log('uploadLabel:', uploadLabel);
    console.log('form:', form);
    
    // Label click to trigger file input
    if (uploadLabel && fileInput) {
        uploadLabel.addEventListener('click', function(e) {
            console.log('Label clicked');
            fileInput.click();
        });
    }
    
    // Drag and drop support
    if (uploadLabel && fileInput) {
        uploadLabel.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadLabel.classList.add('bg-primary-fixed', 'border-primary');
        });
        
        uploadLabel.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadLabel.classList.remove('bg-primary-fixed', 'border-primary');
        });
        
        uploadLabel.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadLabel.classList.remove('bg-primary-fixed', 'border-primary');
            
            // Get files from drop event
            const files = e.dataTransfer.files;
            console.log('Files dropped:', files.length);
            
            // Assign files to input and trigger change event
            const dataTransfer = new DataTransfer();
            for (let i = 0; i < files.length; i++) {
                dataTransfer.items.add(files[i]);
            }
            fileInput.files = dataTransfer.files;
            
            // Trigger the change event
            const changeEvent = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(changeEvent);
        });
    }
    
    // Form submission validation
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submitted');
            const photoInput = document.getElementById('photo-upload-input');
            const photoCount = photoInput ? photoInput.files.length : 0;
            const existingPhotos = document.querySelectorAll('.aspect-\\[3\\/4\\] img[src*="/exchange_books/"]').length;
            const totalPhotos = photoCount + existingPhotos;
            
            console.log('Photo count:', photoCount, 'Existing:', existingPhotos, 'Total:', totalPhotos);
            
            // Get the clicked button
            const submitButton = e.submitter;
            const isContinueBtnClicked = submitButton && 
                                        submitButton.textContent.includes('Pricing');
            
            console.log('Is continue button clicked:', isContinueBtnClicked);
            
            // Only validate photos when continuing to pricing (not for save draft)
            if (isContinueBtnClicked && totalPhotos < 2) {
                e.preventDefault();
                alert('Please upload at least 2 photos before continuing to pricing.');
                return false;
            }
        });
    }
});

