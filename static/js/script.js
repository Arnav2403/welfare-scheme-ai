function startSystem() {
    alert("Welfare Scheme Recommendation System is ready!");
}

document.addEventListener("DOMContentLoaded", function () {

    const progressBars = document.querySelectorAll(".progress");

    progressBars.forEach(function (bar) {

        const score = parseFloat(bar.dataset.score);

        if (!isNaN(score)) {
            bar.style.width = score + "%";
        }

    });

});