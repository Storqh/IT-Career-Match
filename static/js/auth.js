document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-password-confirm]").forEach(confirmInput => {
        const passwordInput = document.getElementById(
            confirmInput.dataset.passwordConfirm
        );

        if (!passwordInput) return;

        const validateMatch = () => {
            confirmInput.setCustomValidity(
                confirmInput.value && confirmInput.value !== passwordInput.value
                    ? "Mật khẩu xác nhận không khớp."
                    : ""
            );
        };

        validateMatch();
        passwordInput.addEventListener("input", validateMatch);
        confirmInput.addEventListener("input", validateMatch);
    });

    const otpInput = document.getElementById("otp");
    const resendButton = document.getElementById("resendBtn");
    const status = document.getElementById("otpStatus");
    const countdown = document.getElementById("countdown");

    if (otpInput) {
        otpInput.addEventListener("input", () => {
            otpInput.value = otpInput.value.replace(/\D/g, "").slice(0, 6);
        });
    }

    if (!resendButton || !status || !countdown) return;

    const originalButtonText = resendButton.textContent.trim();
    let countdownTimer;

    const showStatus = (message, type) => {
        status.className = `alert alert-${type} mt-3 mb-0`;
        status.textContent = message;
        status.setAttribute("role", type === "danger" ? "alert" : "status");
    };

    const startCooldown = (seconds = 60) => {
        window.clearInterval(countdownTimer);
        let remaining = seconds;
        resendButton.disabled = true;

        const updateCountdown = () => {
            if (remaining <= 0) {
                window.clearInterval(countdownTimer);
                resendButton.disabled = false;
                countdown.textContent = "";
                return;
            }

            countdown.textContent = `Bạn có thể gửi lại mã sau ${remaining} giây.`;
            remaining -= 1;
        };

        updateCountdown();
        countdownTimer = window.setInterval(updateCountdown, 1000);
    };

    resendButton.addEventListener("click", async () => {
        resendButton.disabled = true;
        resendButton.setAttribute("aria-busy", "true");
        resendButton.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Đang gửi...';

        try {
            const response = await fetch(resendButton.dataset.resendUrl, {
                method: "POST",
                headers: { Accept: "application/json" },
                credentials: "same-origin"
            });
            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Không gửi được mã OTP. Vui lòng thử lại.");
            }

            showStatus(data.message || "Mã OTP đã được gửi lại.", "success");
            startCooldown();
        } catch (error) {
            showStatus(
                error instanceof Error
                    ? error.message
                    : "Có lỗi xảy ra khi gửi mã OTP. Vui lòng thử lại.",
                "danger"
            );
            resendButton.disabled = false;
        } finally {
            resendButton.removeAttribute("aria-busy");
            resendButton.textContent = originalButtonText;
        }
    });
});
