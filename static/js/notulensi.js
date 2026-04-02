document.addEventListener("DOMContentLoaded", function () {
  const notulensiForm = document.getElementById("notulensiForm");
  const hasilNotulensi = document.getElementById("hasilNotulensi");
  const resultText = document.getElementById("resultText");

  if (notulensiForm) {
    notulensiForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const kegiatan = document.getElementById("kegiatan").value;
      const tempat = document.getElementById("tempat").value;
      const peserta = document.getElementById("peserta").value;

      const html = `
        <h3>NOTULENSI RAPAT</h3>
        <p><strong>Kegiatan:</strong> ${kegiatan}</p>
        <p><strong>Tempat:</strong> ${tempat}</p>
        <p><strong>Peserta:</strong> ${peserta}</p>
        <hr>
        <p><strong>Ringkasan Hasil:</strong></p>
        <p>Hasil transkripsi rapat akan ditampilkan di sini setelah file audio diproses oleh sistem speech-to-text.</p>
      `;

      resultText.innerHTML = html;
      hasilNotulensi.classList.remove("hidden");
    });
  }
});