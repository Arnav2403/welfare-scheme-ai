document.addEventListener("DOMContentLoaded", function () {

    // 1. Fluid progress bar animation & numeric counter
    const scoreSections = document.querySelectorAll(".score-section");
    scoreSections.forEach(function (section) {
        const bar = section.querySelector(".progress");
        const scoreSpan = section.querySelector(".score-text span");
        
        if (bar) {
            const targetScore = parseFloat(bar.dataset.score);
            if (!isNaN(targetScore)) {
                bar.style.width = "0%";
                
                setTimeout(function() {
                    bar.style.width = targetScore + "%";
                }, 150);

                // Fluid number count-up if rankable
                if (scoreSpan && scoreSpan.textContent.includes("%")) {
                    let current = 0;
                    const duration = 900;
                    const startTime = performance.now();

                    function updateCounter(currentTime) {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        // Ease-out cubic
                        const easeOut = 1 - Math.pow(1 - progress, 3);
                        current = easeOut * targetScore;
                        
                        scoreSpan.textContent = current.toFixed(current % 1 === 0 ? 0 : 1) + "%";

                        if (progress < 1) {
                            requestAnimationFrame(updateCounter);
                        } else {
                            scoreSpan.textContent = targetScore + "%";
                        }
                    }

                    setTimeout(function() {
                        requestAnimationFrame(updateCounter);
                    }, 100);
                }
            }
        }
    });

    // 2. Smooth staggered reveal for scheme cards
    const cards = document.querySelectorAll(".scheme-card");
    cards.forEach(function (card, index) {
        card.style.opacity = "0";
        card.style.transform = "translateY(16px)";
        card.style.transition = "opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.16, 1, 0.3, 1)";
        setTimeout(function () {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, 100 + index * 70);
    });

    // 3. Smooth staggered reveal for info cards on home page
    const infoCards = document.querySelectorAll(".info-card");
    infoCards.forEach(function (card, index) {
        card.style.opacity = "0";
        card.style.transform = "translateY(18px)";
        card.style.transition = "opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)";
        setTimeout(function () {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, 180 + index * 100);
    });

    // 4. Fluid accordion animation for details element
    const details = document.querySelectorAll("details");
    details.forEach(function (detail) {
        const summary = detail.querySelector("summary");
        if (summary) {
            summary.addEventListener("click", function () {
                // Gentle bounce micro-interaction
                summary.style.transform = "scale(0.99)";
                setTimeout(function () {
                    summary.style.transform = "";
                }, 120);
            });
        }
    });

    // 5. Button click ripple feedback
    const buttons = document.querySelectorAll("button, .start-button, .back-button, .edit-profile-btn");
    buttons.forEach(function (btn) {
        btn.addEventListener("mousedown", function () {
            this.style.transform = "scale(0.97)";
        });
        btn.addEventListener("mouseup", function () {
            this.style.transform = "";
        });
        btn.addEventListener("mouseleave", function () {
            this.style.transform = "";
        });
    });

});
