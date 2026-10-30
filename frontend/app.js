
// ====================================
// RELOOP INTELLIGENCE
// ====================================

// Format money in Canadian dollars
const money = value =>
  Number(value).toLocaleString("en-CA", {
    style: "currency",
    currency: "CAD"
  });


// ====================================
// ANIMATED DASHBOARD COUNTERS
// ====================================

function animateCounter(element, target, duration = 1200) {
  if (!element) return;

  // Respect reduced-motion accessibility preferences
  if (window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches) {
    element.textContent = target.toLocaleString();
    return;
  }

  const start = performance.now();

  function update(now) {
    const progress = Math.min(
      (now - start) / duration,
      1
    );

    // Smooth ease-out animation
    const eased = 1 - Math.pow(1 - progress, 3);

    const current = Math.round(target * eased);

    element.textContent = current.toLocaleString();

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = target.toLocaleString();
    }
  }

  requestAnimationFrame(update);
}


// ====================================
// HELPER FUNCTIONS
// ====================================

function showError(element, message) {
  element.textContent = message;
  element.classList.remove("hidden");
}

// Safely display user-provided data
function addText(parent, tag, text) {
  const element = document.createElement(tag);
  element.textContent = String(text);
  parent.appendChild(element);
  return element;
}


// ====================================
// BUSINESS DONATION FORM
// ====================================

const form = document.getElementById("donation-form");

if (form) {
  form.addEventListener("submit", async event => {
    event.preventDefault();

    const result = document.getElementById("result");

    result.classList.remove("hidden");
    result.textContent = "Evaluating donation...";

    const donation = {
      company_name:
        document.getElementById("company").value,

      device_type:
        document.getElementById("device").value,

      quantity:
        Number(document.getElementById("quantity").value),

      condition:
        document.getElementById("condition").value,

      uniform_models:
        document.getElementById("uniform").checked,

      pickup_cost:
        Number(document.getElementById("pickup").value)
    };

    try {
      const response = await fetch("/donations", {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify(donation)
      });

      if (!response.ok) {
        throw new Error("Donation could not be saved.");
      }

      const data = await response.json();
      const evaluation = data.evaluation;

      result.replaceChildren();

      addText(result, "h2", "Donation submitted!");

      addText(
        result,
        "p",
        "Reference #" + data.donation_id
      );

      addText(
        result,
        "p",
        "Estimated usable devices: " +
        evaluation.estimated_usable_devices
      );

      addText(
        result,
        "p",
        "Expected revenue: " +
        money(evaluation.estimated_revenue)
      );

      addText(
        result,
        "p",
        "Estimated costs: " +
        money(evaluation.estimated_cost)
      );

      addText(
        result,
        "h3",
        "Estimated contribution: " +
        money(evaluation.estimated_contribution)
      );

      // Financial scenarios
      if (evaluation.scenarios) {
        addText(result, "h3", "Possible outcomes");

        for (const [name, value] of
          Object.entries(evaluation.scenarios)) {

          addText(
            result,
            "p",
            name + ": " +
            money(value.estimated_contribution) +
            " (" +
            value.estimated_usable_devices +
            " usable devices)"
          );
        }
      }

      // Review warnings
      if (evaluation.warnings?.length) {
        addText(result, "h3", "Review notes");

        for (const warning of evaluation.warnings) {
          addText(result, "p", "• " + warning);
        }
      }

      addText(
        result,
        "p",
        "Illustrative estimates only. Staff review required."
      );

      const link = document.createElement("a");

      link.href = "/dashboard";
      link.className = "btn";
      link.textContent = "Open Staff Dashboard";

      result.appendChild(link);

    } catch (error) {
      showError(result, error.message);
    }
  });
}


// ====================================
// STAFF DASHBOARD
// ====================================

const list = document.getElementById("donations-list");

async function loadDonations(animate = true) {
  if (!list) return;

  try {
    const response = await fetch("/donations");

    if (!response.ok) {
      throw new Error("Could not load donations.");
    }

    const donations = await response.json();

    // Animated statistics
    const total = donations.length;

    const pending = donations.filter(
      d => d.status === "Pending"
    ).length;

    const accepted = donations.filter(
      d => d.status === "Accepted"
    ).length;

    if (animate) {
      animateCounter(
        document.getElementById("total"),
        total
      );

      animateCounter(
        document.getElementById("pending"),
        pending
      );

      animateCounter(
        document.getElementById("accepted"),
        accepted
      );
    } else {
      document.getElementById("total").textContent = total;
      document.getElementById("pending").textContent = pending;
      document.getElementById("accepted").textContent = accepted;
    }

    list.replaceChildren();

    if (!donations.length) {
      addText(list, "p", "No donations submitted yet.");
      return;
    }

    // Display donations
    for (const donation of donations) {
      const card = document.createElement("article");
      card.className = "card";

      addText(card, "h3", donation.company_name);

      addText(
        card,
        "p",
        `${donation.quantity} ${donation.device_type}(s) · ` +
        `${donation.condition} condition`
      );

      addText(
        card,
        "p",
        "Status: " + donation.status
      );

      // Re-evaluate saved donation
      const assessmentResponse = await fetch("/evaluate", {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          company_name: donation.company_name,
          device_type: donation.device_type,
          quantity: donation.quantity,
          condition: donation.condition,
          uniform_models: donation.uniform_models,
          pickup_cost: donation.pickup_cost
        })
      });

      if (assessmentResponse.ok) {
        const assessment =
          await assessmentResponse.json();

        addText(
          card,
          "h4",
          "Donation Intelligence"
        );

        addText(
          card,
          "p",
          "Estimated usable devices: " +
          assessment.estimated_usable_devices
        );

        addText(
          card,
          "p",
          "Estimated refurbishment hours: " +
          assessment.estimated_labour_hours
        );

        addText(
          card,
          "p",
          "Expected contribution: " +
          money(assessment.estimated_contribution)
        );

        if (assessment.contribution_per_hour != null) {
          addText(
            card,
            "p",
            "Contribution per labour hour: " +
            money(assessment.contribution_per_hour)
          );
        }

        // Three financial scenarios
        if (assessment.scenarios) {
          const scenarios = document.createElement("div");
          scenarios.className = "scenario-grid";

          for (const [name, value] of
            Object.entries(assessment.scenarios)) {

            const scenario = document.createElement("div");
            scenario.className = "scenario";

            addText(
              scenario,
              "small",
              name.toUpperCase()
            );

            addText(
              scenario,
              "h3",
              money(value.estimated_contribution)
            );

            addText(
              scenario,
              "small",
              value.estimated_usable_devices +
              " potentially usable devices"
            );

            scenarios.appendChild(scenario);
          }

          card.appendChild(scenarios);
        }

        // Display warnings
        if (assessment.warnings?.length) {
          const warningBox =
            document.createElement("div");

          warningBox.className = "warning-box";

          addText(
            warningBox,
            "strong",
            "Review notes"
          );

          for (const warning of assessment.warnings) {
            addText(warningBox, "p", warning);
          }

          card.appendChild(warningBox);
        }
      }

      // Staff decision buttons
      const actions = document.createElement("div");
      actions.className = "donation-actions";

      for (const status of [
        "Pending",
        "Accepted",
        "Declined",
        "Needs Information"
      ]) {
        const button = document.createElement("button");

        button.className = "btn secondary";
        button.textContent = status;
        button.disabled = donation.status === status;

        button.addEventListener("click", async () => {
          try {
            const update = await fetch(
              `/donations/${donation.id}`,
              {
                method: "PATCH",

                headers: {
                  "Content-Type": "application/json"
                },

                body: JSON.stringify({ status })
              }
            );

            if (!update.ok) {
              throw new Error("Status update failed.");
            }

            // Update numbers without restarting animation
            await loadDonations(false);

          } catch (error) {
            alert(error.message);
          }
        });

        actions.appendChild(button);
      }

      card.appendChild(actions);
      list.appendChild(card);
    }

  } catch (error) {
    list.replaceChildren();
    addText(list, "p", error.message);
  }
}

// Load dashboard when opened
loadDonations();
