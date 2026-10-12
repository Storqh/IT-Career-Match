
/* =========================================
   IT CAREER MATCH - GLOBAL UI
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    // 1. Character counters
    document.querySelectorAll("[data-character-count]")
        .forEach(field => {

            const counterId = field.dataset.characterCount;
            const counter = document.getElementById(counterId);

            if (!counter) return;

            const update = () => {
                const length = field.value.length;
                const max = field.maxLength;

                counter.textContent = max > 0
                    ? `${length} / ${max}`
                    : `${length} ký tự`;
            };

            field.addEventListener("input", update);
            update();
        });


    // 2. Submit loading state
    document.querySelectorAll("form[data-loading-form]")
        .forEach(form => {

            form.addEventListener("submit", event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    form.reportValidity();
                    return;
                }

                if (form.dataset.submitting === "true") {
                    event.preventDefault();
                    return;
                }

                form.dataset.submitting = "true";

                const submit = event.submitter ||
                    form.querySelector('[type="submit"]');

                if (!submit) return;

                submit.disabled = true;
                submit.dataset.originalHtml = submit.innerHTML;

                submit.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2"
                          aria-hidden="true"></span>
                    Đang xử lý...
                `;
            });
        });


    // 3. Delete confirmations
    // Add data-confirm="..." to destructive forms.
    document.querySelectorAll("form[data-confirm]")
        .forEach(form => {

            form.addEventListener("submit", event => {
                const message = form.dataset.confirm ||
                    "Bạn có chắc muốn thực hiện thao tác này?";

                if (!window.confirm(message)) {
                    event.preventDefault();
                }
            });
        });


    // 4. Back to top
    const backButton = document.createElement("button");

    backButton.type = "button";
    backButton.className = "icm-back-to-top";
    backButton.setAttribute("aria-label", "Lên đầu trang");
    backButton.innerHTML = '<i class="bi bi-arrow-up"></i>';

    document.body.appendChild(backButton);

    const updateBackButton = () => {
        backButton.classList.toggle(
            "visible",
            window.scrollY > 400
        );
    };

    window.addEventListener("scroll", updateBackButton, {
        passive: true
    });

    updateBackButton();

    backButton.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: window.matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches ? "instant" : "smooth"
        });
    });


    // 5. Restore submit buttons after browser back navigation
    window.addEventListener("pageshow", () => {
        document.querySelectorAll("form[data-loading-form]")
            .forEach(form => {
                form.dataset.submitting = "false";

                form.querySelectorAll(
                    '[type="submit"][data-original-html]'
                ).forEach(button => {
                    button.disabled = false;
                    button.innerHTML = button.dataset.originalHtml;
                });
            });
    });


    // 6. Global toast helper
    window.ICMToast = (message, type = "info") => {
        let container = document.querySelector(
            ".icm-toast-container"
        );

        if (!container) {
            container = document.createElement("div");
            container.className = "icm-toast-container";
            container.setAttribute("aria-live", "polite");
            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.className = `icm-toast ${
            ["success", "error"].includes(type) ? type : ""
        }`;

        const messageElement = document.createElement("span");
        messageElement.textContent = String(message);

        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "icm-toast-close";
        closeButton.setAttribute("aria-label", "Đóng thông báo");
        closeButton.textContent = "×";

        closeButton.addEventListener("click", () => {
            toast.remove();
        });

        toast.append(messageElement, closeButton);
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 4500);
    };

});

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("jobDescriptionSections");
    const addButton = document.getElementById("addDescriptionSection");
    const hiddenField = document.getElementById("description");

    if (!container || !addButton || !hiddenField) return;

    const form = hiddenField.closest("form");

    function addSection(title = "", content = "") {
        const section = document.createElement("div");
        section.className = "job-description-section";

        const header = document.createElement("div");
        header.className = "d-flex justify-content-between align-items-center gap-2 mb-3";

        const heading = document.createElement("strong");
        heading.textContent = "Nội dung tuyển dụng";

        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "btn btn-outline-danger btn-sm";
        remove.innerHTML = '<i class="bi bi-trash"></i> Xóa';

        header.append(heading, remove);

        const titleInput = document.createElement("input");
        titleInput.type = "text";
        titleInput.className = "form-control mb-3 job-section-title";
        titleInput.placeholder = "Tiêu đề: Yêu cầu ứng viên...";
        titleInput.value = title;
        titleInput.required = true;

        const contentInput = document.createElement("textarea");
        contentInput.className = "form-control job-section-content";
        contentInput.rows = 5;
        contentInput.placeholder = "Nhập nội dung chi tiết...";
        contentInput.value = content;
        contentInput.required = true;

        section.append(header, titleInput, contentInput);
        container.appendChild(section);

        remove.addEventListener("click", () => {
            if (container.children.length <= 1) {
                window.ICMToast?.(
                    "Cần giữ ít nhất một mục mô tả.",
                    "error"
                );
                return;
            }
            section.remove();
        });
    }

    addButton.addEventListener("click", () => addSection());

    // Edit Job: nạp nội dung mô tả cũ nếu có
    const initial = document.getElementById("initialJobDescription");
    const existingText = initial ? initial.value : "";

    if (existingText.trim()) {
        addSection("Mô tả công việc", existingText);
    } else {
        addSection("Mô tả công việc", "");
    }

    form?.addEventListener("submit", event => {
        const sections = [...container.querySelectorAll(
            ".job-description-section"
        )];

        const parts = sections.map(section => {
            const title = section.querySelector(
                ".job-section-title"
            ).value.trim();

            const content = section.querySelector(
                ".job-section-content"
            ).value.trim();

            return { title, content };
        });

        if (parts.some(item => !item.title || !item.content)) {
            event.preventDefault();
            window.ICMToast?.(
                "Vui lòng nhập đầy đủ các mục mô tả.",
                "error"
            );
            return;
        }

        hiddenField.value = parts.map(item =>
            `${item.title}\n${item.content}`
        ).join("\n\n");
    }, true);
});

