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
  const nextUrl = params.get("next");

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
        // Verifica se é erro de usuário inativo
        if (data.detail && (data.detail.includes("desativada") || data.detail.includes("inactive") || data.code === "user_inactive")) {
          feedback.innerHTML = `
            <strong>⚠️ Conta Desativada</strong><br>
            Sua conta está desativada. Entre em contato com a administração da biblioteca para reativar seu acesso.
          `;
          feedback.className = "alert alert-warning";
        } else {
          feedback.textContent = data.detail || "Não foi possivel fazer login.";
          feedback.className = "alert alert-error";
        }
        return;
      }

      // Verifica se o usuário está tentando acessar uma rota protegida sem permissão adequada
      const isAdminRoute = nextUrl && (
        nextUrl.includes("/admin/") || 
        nextUrl.includes("/gerenciar") ||
        nextUrl.includes("/api/dashboard/") ||
        nextUrl.includes("/api/usuarios/") ||
        nextUrl.startsWith("/admin/") ||
        nextUrl.match(/\/(admin|reservas\/admin|salas\/admin)\/(dashboard|salas|reserva|usuarios)/)
      );
      
      // Rotas de API que requerem permissão de admin
      const isAdminApiRoute = nextUrl && (
        nextUrl.match(/\/api\/salas\/((?!lookup)[^\/]*)/) || // API de salas exceto lookup
        nextUrl.includes("/admin/reservas/") ||
        nextUrl.includes("/admin/usuarios/")
      );
      
      if ((isAdminRoute || isAdminApiRoute) && !data.is_staff) {
        feedback.innerHTML = `
          <strong>⚠️ Acesso Negado</strong><br>
          Você não tem permissão para acessar áreas administrativas. Redirecionando para suas reservas...
        `;
        feedback.className = "alert alert-warning";
        
        setTimeout(() => {
          window.location.href = data.redirect_url || "/minhas-reservas/";
        }, 2000);
        return;
      }
      
      feedback.textContent = "Login realizado com sucesso. Redirecionando...";
      feedback.className = "alert alert-success";
      
      // Usa redirect_url da API ou nextUrl ou default baseado no tipo de usuário
      const redirectTo = nextUrl || data.redirect_url || (data.is_staff ? "/admin/salas/" : "/minhas-reservas/");
      
      setTimeout(() => {
        window.location.href = redirectTo;
      }, 600);
    } catch (error) {
      // Usa logger condicional se disponível, senão usa console.error padrão
      if (window.logger) {
        window.logger.error("Erro ao autenticar", error);
      } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.error("Erro ao autenticar", error);
      }
      feedback.textContent = "Erro inesperado. Tente novamente.";
      feedback.className = "alert alert-error";
    }
  });
});
