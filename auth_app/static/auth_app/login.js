function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const feedback = document.getElementById("loginFeedback");
  const params = new URLSearchParams(window.location.search);
  const nextUrl = params.get("next") || "/admin/salas/";

  if (window.lucide) {
    window.lucide.createIcons();
  }

  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    feedback.textContent = "";
    feedback.className = "alert d-none";

    const email = (emailInput?.value || "").trim();
    const password = passwordInput?.value || "";

    if (!email || !password) {
      feedback.textContent = "Preencha e-mail e senha.";
      feedback.className = "alert alert-error";
      return;
    }

    try {
      const response = await fetch("/api/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        credentials: "same-origin",
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        feedback.textContent = data.detail || "Não foi possivel fazer login.";
        feedback.className = "alert alert-error";
        return;
      }

      feedback.textContent = "Login realizado com sucesso. Redirecionando...";
      feedback.className = "alert alert-success";
      setTimeout(() => {
        window.location.href = nextUrl;
      }, 600);
    } catch (error) {
      console.error("Erro ao autenticar", error);
      feedback.textContent = "Erro inesperado. Tente novamente.";
      feedback.className = "alert alert-error";
    }
  });
});
