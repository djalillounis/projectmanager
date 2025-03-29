document.addEventListener("DOMContentLoaded", () => {
    const projectForm = document.getElementById("project-info-form");
  
    if (projectForm) {
      projectForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const data = {
          name: document.getElementById("project-name").value,
          description: document.getElementById("project-description").value
        };
  
        fetch(projectForm.action || window.location.pathname + "update_info/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
          },
          body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            document.getElementById("project-title").textContent = data.name || data.description;
            alert("Project updated.");
          }
        });
      });
    }
  });
  
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
  