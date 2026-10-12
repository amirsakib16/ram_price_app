document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("predict-form");
  const submitBtn = document.getElementById("submit-btn");
  const btnText = submitBtn.querySelector(".btn-text");
  const btnLoader = submitBtn.querySelector(".btn-loader");
  const resultSection = document.getElementById("result");
  const errorSection = document.getElementById("error");
  const predictionBadge = document.getElementById("prediction-badge");
  const probaBars = document.getElementById("proba-bars");
  const errorMessage = document.getElementById("error-message");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    resultSection.classList.add("hidden");

    // Collect form data
    const payload = {
      capacity_gb: document.getElementById("capacity_gb").value,
      bus_speed_mhz: document.getElementById("bus_speed_mhz").value,
      demand_ratio: document.getElementById("demand_ratio").value,
      has_discount: document.getElementById("has_discount").value,
      ram_generation: document.getElementById("ram_generation").value,
      condition_clean: document.getElementById("condition_clean").value,
      unit_type: document.getElementById("unit_type").value,
      brand: document.getElementById("brand").value,
      is_ecc: document.getElementById("is_ecc").checked ? 1 : 0,
      is_sodimm: document.getElementById("is_sodimm").checked ? 1 : 0,
      is_gaming: document.getElementById("is_gaming").checked ? 1 : 0,
      is_us_listing: document.getElementById("is_us_listing").checked ? 1 : 0,
      is_bulk_server: document.getElementById("is_bulk_server").checked ? 1 : 0,
    };

    setLoading(true);

    try {
      const res = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || "Prediction failed");
      }

      showResult(data);
    } catch (err) {
      showError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  });

  function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.classList.toggle("hidden", loading);
    btnLoader.classList.toggle("hidden", !loading);
  }

  function showResult(data) {
    const pred = data.prediction;
    const slug = pred.toLowerCase().replace(/\s+/g, "-");

    predictionBadge.textContent = pred;
    predictionBadge.className = "prediction-badge " + slug;

    // Probability bars
    probaBars.innerHTML = "";
    const classes = data.classes || Object.keys(data.probabilities);
    classes.forEach((cls) => {
      const pct = (data.probabilities[cls] || 0) * 100;
      const barSlug = cls.toLowerCase().replace(/\s+/g, "-");

      const row = document.createElement("div");
      row.className = "proba-row";
      row.innerHTML = `
        <span class="proba-label">${cls}</span>
        <div class="proba-track">
          <div class="proba-fill ${barSlug}" style="width: ${pct.toFixed(1)}%"></div>
        </div>
        <span class="proba-value">${pct.toFixed(1)}%</span>
      `;
      probaBars.appendChild(row);
    });

    resultSection.classList.remove("hidden");
    resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorSection.classList.remove("hidden");
  }

  function hideError() {
    errorSection.classList.add("hidden");
  }
});
