document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".alert").forEach(alert => {
    const progress = alert.querySelector(".alert-progress");
    setTimeout(() => { if (progress) progress.style.transform = "scaleX(0)"; }, 100);
    setTimeout(() => {
      alert.classList.remove("show");
      setTimeout(() => alert.remove(), 500);
    }, 3000);
  });
});