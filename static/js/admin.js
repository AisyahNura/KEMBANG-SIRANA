document.addEventListener("DOMContentLoaded", function () {

  const logoutBtn = document.getElementById("logoutBtn");

  if (logoutBtn) {
    logoutBtn.addEventListener("click", function (e) {
      e.preventDefault();

      // hapus data login
      localStorage.removeItem("role");
      localStorage.removeItem("email");

      // kembali ke beranda
      window.location.href = "/";
    });

  }

});