function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function fetchAndPopulateSelectForImages(url, selectElement, callback) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            selectElement.innerHTML = '';
            data.sort((a, b) => a.localeCompare(b));
            data.forEach(item => {
                let option = document.createElement('option');
                option.value = item;
                option.text = capitalizeFirstLetter(item);
                selectElement.add(option);
            });
            if (callback) callback();
        })
        .catch(error => console.error('Error:', error));
}

function updateCultivatorOptionsForImages() {
    let productTypeSelectImage = document.getElementById('productTypeSelectedImage');
    let selectedProductType = capitalizeFirstLetter(productTypeSelectImage.value);
    let cultivatorSelect = document.getElementById('cultivatorSelectedImage')
    let url = '/search/cultivators/' + selectedProductType;
    fetchAndPopulateSelectForImages(url, cultivatorSelect, updateStrainOptionsForImages);
}

function updateStrainOptionsForImages() {
    let productTypeSelectImage = document.getElementById('productTypeSelectedImage');
    let selectedProductType = capitalizeFirstLetter(productTypeSelectImage.value);
    let cultivatorSelect = document.getElementById('cultivatorSelectedImage')
    let selectedCultivator = cultivatorSelect.value;
    let url = '/search/strains/' + selectedProductType + '/' + selectedCultivator;
    fetchAndPopulateSelectForImages(url, document.getElementById('strainSelectedImage'));
}

async function fetchProductImages(event) {
    if (event) { event.preventDefault() };
    const productType = document.getElementById('productTypeSelectedImage').value;
    const strain = document.getElementById('strainSelectedImage').value;
    const cultivator = document.getElementById('cultivatorSelectedImage').value;

    const url = `/images/get_all?product_type=${encodeURIComponent(productType)}&strain=${encodeURIComponent(strain)}&cultivator=${encodeURIComponent(cultivator)}`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        let images = [];
        for (let type in data) {
            if (data.hasOwnProperty(type)) {
                const productObj = data[type];
                for (let productId in productObj) {
                    if (productObj.hasOwnProperty(productId)) {
                        const imageMap = productObj[productId];
                        for (let imagePath in imageMap) {
                            if (imageMap.hasOwnProperty(imagePath)) {
                                images.push({
                                    productType: type,
                                    productId: productId,
                                    imagePath: imagePath,
                                    imageUrl: imageMap[imagePath]
                                });
                            }
                        }
                    }
                }
            }
        }
        const container = document.getElementById('imageSelectContainer');
        container.innerHTML = '';

        if (images.length === 0) {
            container.innerHTML = '<p>No images found.</p>';
            return;
        }

        const optionsRow = document.createElement('div');
        optionsRow.classList.add("row", "align-items-center", "g-2", "mb-3");

        const selectCol = document.createElement('div');
        selectCol.classList.add("col-12", "col-md-6", "col-lg-8");

        const select = document.createElement('select');
        select.id = 'imageSelect';
        select.classList.add("form-select");

        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.text = 'Select an image';
        select.appendChild(defaultOption);
        images.forEach(image => {
            const option = document.createElement('option');
            option.value = image.imageUrl;
            option.text = image.imagePath.split('/').pop();;
            option.setAttribute('data-product-type', image.productType);
            option.setAttribute('data-product-id', image.productId);
            option.setAttribute('data-image-path', image.imagePath);
            select.appendChild(option);
        });

        selectCol.appendChild(select);
        optionsRow.appendChild(selectCol);

        const removeImageCol = document.createElement('div');
        removeImageCol.classList.add("col-6", "col-lg-3");

        const removeImageBtn = document.createElement('button');
        removeImageBtn.id = 'removeImageBtn';
        removeImageBtn.type = 'button';
        removeImageBtn.classList.add("btn", "btn-danger", "w-100");
        removeImageBtn.textContent = 'Remove Image';
        removeImageBtn.disabled = true;
        removeImageBtn.addEventListener('click', function() {
          alert('Remove Image action triggered!');
        });

        removeImageCol.appendChild(removeImageBtn);
        //optionsRow.appendChild(removeImageCol);

        const makePrimaryCol = document.createElement('div');
        makePrimaryCol.classList.add("col-12", "col-md-6", "col-lg-4");

        const makePrimaryBtn = document.createElement('button');
        makePrimaryBtn.id = 'makePrimaryBtn';
        makePrimaryBtn.type = 'button';
        makePrimaryBtn.classList.add("btn", "btn-warning", "w-100");
        makePrimaryBtn.textContent = 'Make Primary';
        makePrimaryBtn.disabled = true;
        makePrimaryBtn.addEventListener('click', updatePrimaryImage);

        makePrimaryCol.appendChild(makePrimaryBtn);
        optionsRow.appendChild(makePrimaryCol);

        container.appendChild(optionsRow);

        const imgContainer = document.createElement('div');
        imgContainer.classList.add("col-12", "col-lg-6", "mx-auto", "py-3");

        const imgPreview = document.createElement('img');
        imgPreview.id = 'imagePreview';
        imgPreview.style.maxWidth = '100%';
        imgPreview.style.display = 'none';
        imgPreview.className = 'mb-3';

        imgContainer.appendChild(imgPreview);
        container.appendChild(imgContainer);

        select.addEventListener('change', function() {
            const selectedUrl = select.value;
            if (selectedUrl) {
                imgPreview.src = selectedUrl;
                imgPreview.style.display = 'block';
                makePrimaryBtn.disabled = false;
                removeImageBtn.disabled = false;
            } else {
                imgPreview.src = '';
                imgPreview.style.display = 'none';
                makePrimaryBtn.disabled = true;
                removeImageBtn.disabled = true;
            }
        });
    } catch (error) {
        console.error('Error fetching images:', error);
    }
}

async function updatePrimaryImage() {
  const imageSelect = document.getElementById('imageSelect');
  if (!imageSelect) {
    alert("Image select element not found.");
    return;
  }
  const selectedOption = imageSelect.options[imageSelect.selectedIndex];
  if (!selectedOption || !selectedOption.getAttribute('data-image-path')) {
    alert("Please select an image.");
    return;
  }

  if (!confirm("Are you sure you wnat to update the primary image?")) {return; };

  const productType = document.getElementById('productTypeSelectedImage').value;
  const productId = selectedOption.getAttribute('data-product-id');
  const cardPath = selectedOption.getAttribute('data-image-path');

  const url = `/images/make_primary?product_type=${encodeURIComponent(productType)}&product_id=${encodeURIComponent(productId)}&card_path=${encodeURIComponent(cardPath)}`;
  const authToken = await window.supabaseClient.getAccessToken();
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${authToken}`
      }
    });
    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }
    const result = await response.json();
    alert("Primary image updated successfully!");
    await fetchProductImages();
  } catch (error) {
    console.error("Error updating primary image:", error);
    alert("Failed to update primary image.");
  }
}

async function convertAndCompressImageForSafeUpload(file) {
  const options = {
    maxSizeMB: 1,
    maxWidthOrHeight: 1024,
    useWebWorker: true,
    fileType: 'image/webp'
  };
  try {
    const compressedBlob = await window.imageCompression(file, options);
    const webpFile = new File(
      [compressedBlob],
      file.name.replace(/\.[^/.]+$/, '') + '.webp',
      { type: 'image/webp' }
    );
    return webpFile;
  } catch (err) {
    console.error('Compression failed:', err);
    return null;
  }
}

async function uploadImagesForProduct() {
    const imageSelect = document.getElementById('imageSelect');
    if (!imageSelect) {
      alert("Image select element not found.");
      return;
    }
    const selectedOption = imageSelect.options[1];
    if (!selectedOption || !selectedOption.getAttribute('data-image-path')) {
      alert("Error selecting an image.");
      return;
    }
    const productId = selectedOption.getAttribute('data-product-id');
    if (!productId) {
        alert('Please select a product type, cultivator, and strain first.');
        return;
    }
    const productType = document.getElementById('productTypeSelectedImage').value;
    const fileInput = document.getElementById('productImageUpload');
    const files = fileInput.files;

    if (!files || files.length === 0) {
        alert('Please select at least one image.');
        return;
    }
    const uploadUrl = `/images/${productType}/${productId}/upload/`;
    const selectedFiles = Array.from(files).slice(0, 5);
    if (files.length > 3) {
        alert('You selected more than 5 images — only the first 5 will be uploaded.');
    }
    const authToken = await window.supabaseClient.getAccessToken();
    if (!confirm("Are you sure you wnat to add these images to the selected product?")) {return; };
    const uploadPromises = selectedFiles.map(async (originalFile) => {
        const formData = new FormData();
        const validatedImage = await convertAndCompressImageForSafeUpload(originalFile);

        if (validatedImage) {
            formData.append('file', validatedImage);

            return fetch(uploadUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                }
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.error || (data.message && data.message.includes('unsafe'))) {
                    throw new Error(data.error || data.message);
                }
                return data;
            });
        } else {
            throw new Error(`Image compression failed for ${originalFile.name}`);
        }
    });

    try {
      await Promise.all(uploadPromises);
      alert('Strain and images successfully submitted!');
    } catch (err) {
      console.error('Image upload failed:', err);
      alert(`Submission completed, but image upload failed: ${err.message}`);
    }
}


window.addEventListener('DOMContentLoaded', function() {
  let productTypeSelectImage = document.getElementById('productTypeSelectedImage');
  let cultivatorSelect = document.getElementById('cultivatorSelectedImage');
  let strainSelect = document.getElementById('strainSelectedImage');
  let updateImagesForm = document.getElementById('manageImagesForm');


  productTypeSelectImage.addEventListener('change', updateCultivatorOptionsForImages);
  cultivatorSelect.addEventListener('change', updateStrainOptionsForImages);

  fetchAndPopulateSelectForImages('/search/product-types', productTypeSelectImage, function() {
      updateCultivatorOptionsForImages();
  });

  document.getElementById('getImagesButton').addEventListener('click', fetchProductImages);
  document.addEventListener('click', function (e) {
    const strainCard = document.getElementById('strainSubmissionFormCard');
    const imageCard = document.getElementById('manageImagesFormCard');

    if (e.target && e.target.id === 'toggleImagesFormButton') {
      strainCard.classList.add('d-none');
      imageCard.classList.remove('d-none');
      imageCard.style.display = 'block';
      imageCard.offsetHeight;
    }
    if (e.target && e.target.id === 'toggleStrainsFormButton') {
      imageCard.classList.add('d-none');
      strainCard.classList.remove('d-none');
      strainCard.style.display = 'block';
      strainCard.offsetHeight;
    }
  });
  document.getElementById('getImagesButton').addEventListener('click', fetchProductImages);
  document.getElementById('uploadProductImagesButton').addEventListener('click', async () => {
    await uploadImagesForProduct();
  });

});
