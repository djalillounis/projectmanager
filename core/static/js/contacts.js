document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contact-form");
    if (contactForm) {
      contactForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(this);
  
        fetch(this.getAttribute("action") || window.location.pathname + "contacts/add/", {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") },
          body: formData
        }).then(res => res.json())
          .then(data => {
            if (data.success && data.contact_html) {
              const container = document.getElementById("contacts-container");
              const temp = document.createElement("div");
              temp.innerHTML = data.contact_html.trim();
              container.prepend(temp.firstElementChild);
              contactForm.reset();
  
              const alert = document.createElement("div");
              alert.className = "alert alert-success mt-2";
              alert.innerText = "Contact added successfully!";
              contactForm.prepend(alert);
              setTimeout(() => alert.remove(), 3000);
  
              rebindContactEvents();  // Bind handlers for the new contact
            } else {
              alert("Error: " + JSON.stringify(data.errors || "Unexpected error"));
            }
          });
      });
    }
  
    rebindContactEvents();  // Initial binding
  });
  
  function rebindContactEvents() {
    document.querySelectorAll(".edit-contact-btn").forEach(btn => {
      btn.onclick = function () {
        const panel = btn.closest(".contact-card").querySelector(".edit-contact-panel");
        panel.classList.toggle("d-none");
      };
    });
  
    document.querySelectorAll(".edit-contact-form").forEach(form => {
      form.onsubmit = function (e) {
        e.preventDefault();
        const contactId = form.dataset.id;
        const formData = new FormData(form);
  
        fetch(`/contacts/${contactId}/update/`, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") },
          body: formData
        }).then(res => res.json()).then(data => {
          if (data.success) {
            const panel = form.closest(".edit-contact-panel");
            panel.classList.add("d-none");
  
            const alert = document.createElement("div");
            alert.className = "alert alert-success mt-2";
            alert.innerText = "Contact updated successfully!";
            form.parentElement.prepend(alert);
            setTimeout(() => alert.remove(), 3000);
          } else {
            alert("Update failed.");
          }
        });
      };
  
      const deleteBtn = form.querySelector(".delete-contact-btn");
      if (deleteBtn) {
        deleteBtn.onclick = function () {
          const contactId = form.dataset.id;
          if (!confirm("Are you sure you want to delete this contact?")) return;
  
          fetch(`/contacts/${contactId}/delete/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") }
          }).then(res => res.json()).then(data => {
            if (data.success) {
              document.getElementById(`contact-${contactId}`).remove();
            } else {
              alert("Failed to delete contact.");
            }
          });
        };
      }
    });
  }
  
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  