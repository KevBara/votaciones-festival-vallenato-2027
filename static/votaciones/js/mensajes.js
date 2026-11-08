document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".message.auto-dismiss").forEach((message) => {
        window.setTimeout(() => {
            message.classList.add("message-hidden");
            window.setTimeout(() => message.remove(), 350);
        }, 4000);
    });
});
