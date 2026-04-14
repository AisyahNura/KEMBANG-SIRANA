document.addEventListener("DOMContentLoaded", function () {
  // Progress simulation untuk UX yang lebih baik
  let progressInterval;
  const steps = [
    { text: "Memuat model AI...", percent: 10 },
    { text: "Memproses audio...", percent: 30 },
    { text: "Melakukan transkripsi...", percent: 60 },
    { text: "Membersihkan teks...", percent: 75 },
    { text: "Membuat ringkasan...", percent: 90 },
    { text: "Finalisasi dokumen...", percent: 100 }
  ];

  window.showLoading = function() {
    const loadingDiv = document.getElementById('loadingText');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const currentStep = document.getElementById('currentStep');
    const submitBtn = document.getElementById('submitBtn');

    // Sembunyikan tombol submit
    submitBtn.style.display = 'none';

    // Tampilkan loading
    loadingDiv.style.display = 'block';

    let currentStepIndex = 0;
    let currentProgress = 0;

    progressInterval = setInterval(() => {
      if (currentStepIndex < steps.length) {
        const step = steps[currentStepIndex];
        currentProgress = Math.min(currentProgress + 2, step.percent);

        progressBar.style.width = currentProgress + '%';
        progressText.textContent = Math.round(currentProgress) + '%';
        currentStep.textContent = step.text;

        if (currentProgress >= step.percent) {
          currentStepIndex++;
        }
      } else {
        // Selesai
        clearInterval(progressInterval);
        currentStep.textContent = "Proses selesai! Menampilkan hasil...";
      }
    }, 500);
  };

  // Fallback untuk form submission
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', function(e) {
      // Jika showLoading belum dipanggil dari onsubmit
      if (typeof window.showLoading === 'function') {
        window.showLoading();
      }
    });
  }
});