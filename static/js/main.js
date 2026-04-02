console.log("SIRANA KEMBANG ready");

// =========================
// PREVIEW UNDANGAN
// =========================
const undanganForm = document.getElementById("undanganForm");

if (undanganForm) {
  undanganForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const kegiatan = document.getElementById("kegiatan").value;
    const tempat = document.getElementById("tempat").value;
    const tanggal = document.getElementById("tanggal").value;
    const waktu = document.getElementById("waktu").value;
    const peserta = document.getElementById("peserta").value;
    const anggaran = document.getElementById("anggaran").value;

    const nomorSurat = "00" + Math.floor(Math.random() * 100) + "/SKR/I/2026";

    const template = `
      <div class="kop">
        <h2>PEMERINTAH KABUPATEN JOMBANG</h2>
        <h3>KEMENTERIAN AGAMA KABUPATEN JOMBANG</h3>
        <p>Jl. Contoh No. 123 Telp. (031) 123456</p>
        <hr>
      </div>

      <p>
        <strong>Nomor:</strong> ${nomorSurat}<br>
        <strong>Lampiran:</strong> -<br>
        <strong>Perihal:</strong> Undangan ${kegiatan}
      </p>

      <p>Yth. ${peserta}<br>di Tempat</p>

      <p>Dengan hormat,</p>

      <p>
        Sehubungan dengan akan dilaksanakannya <strong>${kegiatan}</strong>,
        kami mengundang Bapak/Ibu untuk hadir pada:
      </p>

      <table>
        <tr><td>Hari/Tanggal</td><td>: ${tanggal}</td></tr>
        <tr><td>Waktu</td><td>: ${waktu}</td></tr>
        <tr><td>Tempat</td><td>: ${tempat}</td></tr>
        <tr><td>Peserta</td><td>: ${peserta}</td></tr>
        <tr><td>Anggaran</td><td>: ${anggaran}</td></tr>
      </table>

      <p>
        Demikian undangan ini kami sampaikan.
        Atas perhatian dan kehadirannya diucapkan terima kasih.
      </p>

      <br><br>
      <p>Hormat kami,</p>
      <br><br><br>
      <p><strong>Ketua Panitia</strong></p>
    `;

    document.getElementById("templateResult").innerHTML = template;
    document.getElementById("previewSection").classList.remove("hidden");
  });
}