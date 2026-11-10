document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("chatbotToggle");
    const close = document.getElementById("chatbotClose");
    const resetButton = document.getElementById("chatbotReset");
    const windowEl = document.getElementById("chatbotWindow");
    const messages = document.getElementById("chatbotMessages");
    const form = document.getElementById("chatbotForm");
    const input = document.getElementById("chatbotInput");
    const sendButton = document.getElementById("chatbotSend");
    const suggestions = document.getElementById("chatbotSuggestions");

    if (
        !toggle || !close || !windowEl ||
        !messages || !form || !input || !sendButton
    ) {
        return;
    }

    const STORAGE_KEY = "it_career_match_chatbot_state_v1";
    const initialMessagesHTML = messages.innerHTML;
    const initialSuggestionsHTML = suggestions ? suggestions.innerHTML : "";

    let busy = false;
    let historyItems = [];
    let currentSuggestions = null;

    function saveState() {
        try {
            sessionStorage.setItem(
                STORAGE_KEY,
                JSON.stringify({
                    open: !windowEl.hidden,
                    history: historyItems.slice(-30),
                    suggestions: currentSuggestions
                })
            );
        } catch (err) {
            // Bỏ qua lỗi nếu trình duyệt chặn sessionStorage
        }
    }

    function restoreState() {
        try {
            const raw = sessionStorage.getItem(STORAGE_KEY);
            if (!raw) return;

            const parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== "object") return;

            if (Array.isArray(parsed.history) && parsed.history.length > 0) {
                historyItems = parsed.history;
                messages.innerHTML = initialMessagesHTML;
                for (const entry of historyItems) {
                    renderMessageDOM(
                        entry.text,
                        entry.role,
                        entry.actions || []
                    );
                }
            }

            if (Array.isArray(parsed.suggestions) && parsed.suggestions.length > 0) {
                currentSuggestions = parsed.suggestions;
                renderSuggestions(parsed.suggestions);
            }

            if (parsed.open) {
                setOpen(true, false);
            }
        } catch (err) {
            // Bỏ qua lỗi khôi phục
        }
    }

    function setOpen(open, shouldSave = true) {
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

        if (shouldSave) {
            saveState();
        }
    }

    toggle.addEventListener("click", () => {
        setOpen(windowEl.hidden);
    });

    close.addEventListener("click", () => setOpen(false));

    resetButton?.addEventListener("click", async () => {
        if (busy) return;

        historyItems = [];
        currentSuggestions = null;
        messages.innerHTML = initialMessagesHTML;
        if (suggestions) {
            suggestions.innerHTML = initialSuggestionsHTML;
        }
        try {
            sessionStorage.removeItem(STORAGE_KEY);
        } catch (err) {
            // ignore
        }

        try {
            await fetch("/api/chatbot/reset", {
                method: "POST",
                credentials: "same-origin"
            });
        } catch (err) {
            // ignore
        }

        input.focus();
        scrollToBottom();
    });

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

    function renderMessageDOM(text, role = "bot", actions = []) {
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

        const textDiv = document.createElement("div");
        textDiv.className = "chatbot-bubble-text";
        textDiv.textContent = text;
        bubble.appendChild(textDiv);

        if (role === "bot" && Array.isArray(actions) && actions.length > 0) {
            const actionsContainer = document.createElement("div");
            actionsContainer.className = "chatbot-actions";

            for (const act of actions) {
                if (!act || !act.label || !act.url) continue;

                const link = document.createElement("a");
                link.className = "chatbot-action-link";
                link.href = act.url;
                link.textContent = act.label;
                actionsContainer.appendChild(link);
            }

            if (actionsContainer.childNodes.length > 0) {
                bubble.appendChild(actionsContainer);
            }
        }

        item.appendChild(bubble);
        messages.appendChild(item);

        scrollToBottom();
        return item;
    }

    function addMessage(text, role = "bot", actions = []) {
        const item = renderMessageDOM(text, role, actions);
        historyItems.push({
            text,
            role,
            actions: Array.isArray(actions) ? actions : []
        });
        saveState();
        return item;
    }

    function renderSuggestions(suggestionList) {
        if (!suggestions || !Array.isArray(suggestionList) || suggestionList.length === 0) {
            return;
        }

        suggestions.innerHTML = "";
        for (const q of suggestionList) {
            if (typeof q !== "string" || !q.trim()) continue;

            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "chatbot-suggestion";
            btn.dataset.question = q.trim();

            const icon = document.createElement("i");
            icon.className = "bi bi-chat-right-text";
            btn.appendChild(icon);
            btn.appendChild(document.createTextNode(" " + q.trim()));

            suggestions.appendChild(btn);
        }
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

            if (Array.isArray(data.suggestions) && data.suggestions.length > 0) {
                currentSuggestions = data.suggestions;
                renderSuggestions(data.suggestions);
            }

            addMessage(
                data.reply || "Mình chưa có câu trả lời phù hợp.",
                "bot",
                data.actions || []
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

    restoreState();
});
