
document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("chatbotToggle");
    const close = document.getElementById("chatbotClose");
    const windowEl = document.getElementById("chatbotWindow");
    const messages = document.getElementById("chatbotMessages");
    const form = document.getElementById("chatbotForm");
    const input = document.getElementById("chatbotInput");
    const sendButton = document.getElementById("chatbotSend");
    const suggestions = document.getElementById("chatbotSuggestions");

    if (!toggle || !close || !windowEl ||
        !messages || !form || !input || !sendButton) {
        return;
    }

    let busy = false;

    function setOpen(open) {
        windowEl.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
        toggle.setAttribute(
            "aria-label",
            open ? "Đóng trợ lý hướng nghiệp" : "Mở trợ lý hướng nghiệp"
        );

        if (open) {
            input.focus();
            scrollToBottom();
        }
    }

    toggle.addEventListener("click", () => {
        setOpen(windowEl.hidden);
    });

    close.addEventListener("click", () => setOpen(false));

    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && !windowEl.hidden) {
            setOpen(false);
            toggle.focus();
        }
    });

   

    function scrollToBottom() {
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                messages.scrollTop = messages.scrollHeight;
            });
        });
    }


    function addMessage(text, role = "bot") {
        const item = document.createElement("div");
        item.className = `chatbot-message ${role}`;

        if (role === "bot") {
            const avatar = document.createElement("div");
            avatar.className = "chatbot-message-avatar";

            const icon = document.createElement("i");
            icon.className = "bi bi-robot";

            avatar.appendChild(icon);
            item.appendChild(avatar);
        }

        const bubble = document.createElement("div");
        bubble.className = "chatbot-bubble";

        // textContent giúp tránh thực thi HTML từ tin nhắn.
        bubble.textContent = text;

        item.appendChild(bubble);
        messages.appendChild(item);

        scrollToBottom();
        return item;
    }

    function showTyping() {
        const item = document.createElement("div");
        item.className = "chatbot-message bot";

        const avatar = document.createElement("div");
        avatar.className = "chatbot-message-avatar";
        avatar.innerHTML = '<i class="bi bi-robot"></i>';

        const bubble = document.createElement("div");
        bubble.className = "chatbot-bubble";

        const typing = document.createElement("div");
        typing.className = "chatbot-typing";
        typing.setAttribute("aria-label", "Đang trả lời");

        for (let i = 0; i < 3; i++) {
            typing.appendChild(document.createElement("span"));
        }

        bubble.appendChild(typing);
        item.append(avatar, bubble);
        messages.appendChild(item);

        scrollToBottom();
        return item;
    }

    async function sendMessage(question) {
        question = question.trim();

        if (!question || busy) return;

        busy = true;
        input.value = "";
        input.disabled = true;
        sendButton.disabled = true;

        addMessage(question, "user");
        const typing = showTyping();

        try {
            const response = await fetch("/api/chatbot", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "same-origin",
                body: JSON.stringify({
                    message: question
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Không thể xử lý câu hỏi."
                );
            }

            typing.remove();
            addMessage(
                data.reply || "Mình chưa có câu trả lời phù hợp."
            );
            scrollToBottom();
        } catch (error) {
            typing.remove();

            addMessage(
                "Xin lỗi, chatbot đang gặp sự cố. " +
                "Vui lòng thử lại sau."
            );
            scrollToBottom();
            console.error("Chatbot error:", error);

        } finally {
            busy = false;
            input.disabled = false;
            sendButton.disabled = false;

            if (!windowEl.hidden) {
                input.focus();
            }
        }
    }

    form.addEventListener("submit", event => {
        event.preventDefault();
        sendMessage(input.value);
    });

    suggestions?.addEventListener("click", event => {
        const button = event.target.closest("[data-question]");
        if (!button) return;

        sendMessage(button.dataset.question);
    });
});
