const fileInput = document.querySelector('input[type="file"]');
const imageBox = document.querySelector('.box:first-child');
const textarea = document.querySelector('textarea');
const msgBox = document.createElement('p');
msgBox.style.color = '#fff';
msgBox.style.marginTop = '10px';
textarea.parentNode.appendChild(msgBox);

// Görsel önizleme
fileInput.addEventListener('change', function (event) {
  const file = event.target.files[0];
  if (file && file.type.startsWith('image/')) {
    const oldImg = imageBox.querySelector('img');
    if (oldImg) imageBox.removeChild(oldImg);

    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.style.maxWidth = '100%';
    img.style.maxHeight = '100px';
    img.style.marginTop = '10px';
    imageBox.appendChild(img);
  }
});

// Mesaj kutusu
textarea.addEventListener('input', function () {
  msgBox.textContent = "Gizlenecek mesaj: " + textarea.value;
});

// Encode butonu
const compareButton = document.createElement("button");
compareButton.textContent = "İncele";
compareButton.style.marginTop = "1.5rem";
compareButton.style.display = "none";
compareButton.onclick = () => {
  const original = compareButton.getAttribute("data-original");
  const encoded = compareButton.getAttribute("data-encoded");
  if (original && encoded) {
    window.open(`compare.html?original=${encodeURIComponent(original)}&encoded=${encodeURIComponent(encoded)}`, '_blank');
  }
};
document.querySelector(".container").appendChild(compareButton);

document.getElementById("encode-btn").addEventListener("click", async () => {
  if (!fileInput.files[0] || !textarea.value.trim()) {
    alert("Lütfen bir resim ve mesaj giriniz.");
    return;
  }

  const formData = new FormData();
  formData.append("image", fileInput.files[0]);
  formData.append("message", textarea.value.trim());

  const applyHistogram = document.getElementById("histogramCheck")?.checked || false;
  formData.append("histogram", applyHistogram ? "1" : "0");

  try {
    const response = await fetch("http://127.0.0.1:5000/encode", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.status === "success") {
      document.getElementById("previewImage").src = data.preview_url;
      document.getElementById("downloadOriginal").href = data.download_url;
      document.getElementById("downloadPreview").href = data.preview_url;

      const stats = `Mesaj uzunluğu: ${data.message_length} karakter<br>
        Kullanılan bit sayısı: ${data.used_pixels * 3}<br>
        Toplam kanal sayısı: ${data.total_pixels * 3}`;
      document.getElementById("statsMessage").innerHTML = stats;

      const progressBar = document.getElementById("bitProgressBar");
      const ratio = data.bit_used_ratio;
      const safeRatio = Math.max(ratio, 0.5);
      progressBar.style.width = safeRatio + "%";
      progressBar.textContent = ratio.toFixed(2) + "%";

      const bitplaneList = document.getElementById("bitplaneList");
      bitplaneList.innerHTML = "";
      if (data.bitplanes && Array.isArray(data.bitplanes)) {
        data.bitplanes.forEach((url) => {
          const img = document.createElement("img");
          img.src = url;
          bitplaneList.appendChild(img);
        });
      }

      // İncele butonu göster
      compareButton.setAttribute("data-original", data.original_url || data.download_url);
      compareButton.setAttribute("data-encoded", data.preview_url);
      compareButton.style.display = "inline-block";

      document.getElementById("resultSection").style.display = "block";

    } else {
      alert("Hata: " + data.message);
    }

  } catch (err) {
    console.error("Encode işlemi sırasında hata:", err);
    alert("Sunucuya ulaşılamadı.");
  }
});
