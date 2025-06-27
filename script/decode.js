const decodeFileInput = document.getElementById("decodeImageInput");
const resultBox = document.getElementById("decodedMessageBox");
const resultContainer = document.getElementById("decodedResult");
const previewImage = document.getElementById("previewImage");

// Önizleme
decodeFileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file && file.type.startsWith("image/")) {
    previewImage.src = URL.createObjectURL(file);
    previewImage.style.display = "block";
  }
});

// Decode işlemi
document.getElementById("decode-btn").addEventListener("click", async () => {
  if (!decodeFileInput.files[0]) {
    alert("Lütfen bir resim yükleyin.");
    return;
  }

  const formData = new FormData();
  formData.append("image", decodeFileInput.files[0]);

  try {
    const response = await fetch("http://localhost:5000/decode", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.status === "success") {
      resultBox.textContent = data.message;
    } else {
      resultBox.textContent = data.message || "Mesaj çözülemedi.";
    }
    resultContainer.style.display = "block";

  } catch (error) {
    console.error("Decode error:", error);
    resultBox.textContent = "Sunucuya ulaşılamadı.";
    resultContainer.style.display = "block";
  }
});
