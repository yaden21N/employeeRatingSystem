function apiUrl(path) {
  var base = window.EMPLOYEE_API_BASE || "";
  return base + path;
}

function apiHeaders(includeJson) {
  var headers = {};
  if (includeJson) {
    headers["Content-Type"] = "application/json";
  }
  var token = getIdToken();
  if (token) {
    headers.Authorization = "Bearer " + token;
  }
  return headers;
}

function apiFetch(url, options) {
  options = options || {};
  if (!options.headers) {
    options.headers = apiHeaders(Boolean(options.body));
  }
  return fetch(url, options).then(function (response) {
    if (response.status === 401) {
      setIdToken("");
      refreshAuthView();
      setStatus("Please log in again.", "error");
    }
    return response;
  });
}

function refreshAuthView() {
  var authSection = document.getElementById("auth-section");
  var appMain = document.getElementById("app-main");
  var signup = document.getElementById("signup-form");
  var confirm = document.getElementById("confirm-form");
  var login = document.getElementById("login-form");
  var loggedInAs = document.getElementById("logged-in-as");
  var logoutButton = document.getElementById("logout-button");

  if (!cognitoIsOn()) {
    authSection.hidden = true;
    appMain.hidden = false;
    return;
  }

  authSection.hidden = false;
  if (getIdToken()) {
    signup.hidden = true;
    confirm.hidden = true;
    login.hidden = true;
    loggedInAs.hidden = false;
    loggedInAs.textContent = "You are logged in.";
    logoutButton.hidden = false;
    appMain.hidden = false;
  } else {
    signup.hidden = false;
    confirm.hidden = false;
    login.hidden = false;
    loggedInAs.hidden = true;
    logoutButton.hidden = true;
    appMain.hidden = true;
  }
}

function averageScore(ratings) {
  if (ratings.length === 0) {
    return "none yet";
  }

  var total = 0;
  var i = 0;
  while (i < ratings.length) {
    total = total + ratings[i].score;
    i = i + 1;
  }
  var average = total / ratings.length;
  return average.toFixed(1) + " / 5";
}

function setStatus(message, kind) {
  var status = document.getElementById("status");
  status.textContent = message;
  status.className = kind || "";
}

function readError(data, fallback) {
  if (data && data.error) {
    return data.error;
  }
  return fallback;
}

function showEmployees(employees) {
  var empty = document.getElementById("empty-list");
  var table = document.getElementById("employee-table");
  var rows = document.getElementById("employee-rows");
  rows.innerHTML = "";

  if (employees.length === 0) {
    empty.hidden = false;
    table.hidden = true;
    return;
  }

  empty.hidden = true;
  table.hidden = false;

  var i = 0;
  while (i < employees.length) {
    var employee = employees[i];
    var row = document.createElement("tr");

    var idCell = document.createElement("td");
    idCell.textContent = employee.id;
    row.appendChild(idCell);

    var nameCell = document.createElement("td");
    nameCell.textContent = employee.name;
    row.appendChild(nameCell);

    var deptCell = document.createElement("td");
    deptCell.textContent = employee.department;
    row.appendChild(deptCell);

    var titleCell = document.createElement("td");
    titleCell.textContent = employee.job_title;
    row.appendChild(titleCell);

    var emailCell = document.createElement("td");
    emailCell.textContent = employee.email;
    row.appendChild(emailCell);

    var ratingCell = document.createElement("td");
    ratingCell.textContent = averageScore(employee.ratings);
    row.appendChild(ratingCell);

    var actionCell = document.createElement("td");

    var rateButton = document.createElement("button");
    rateButton.type = "button";
    rateButton.textContent = "Rate";
    rateButton.setAttribute("data-id", employee.id);
    rateButton.addEventListener("click", function () {
      document.getElementById("rate-id").value = this.getAttribute("data-id");
      document.getElementById("rate-score").focus();
    });
    actionCell.appendChild(rateButton);

    var editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "Edit";
    editButton.setAttribute("data-id", employee.id);
    editButton.setAttribute("data-name", employee.name);
    editButton.setAttribute("data-department", employee.department);
    editButton.setAttribute("data-job-title", employee.job_title);
    editButton.setAttribute("data-email", employee.email);
    editButton.addEventListener("click", function () {
      document.getElementById("edit-id").value = this.getAttribute("data-id");
      document.getElementById("edit-name").value = this.getAttribute("data-name");
      document.getElementById("edit-department").value = this.getAttribute("data-department");
      document.getElementById("edit-job-title").value = this.getAttribute("data-job-title");
      document.getElementById("edit-email").value = this.getAttribute("data-email");
      document.getElementById("edit-name").focus();
    });
    actionCell.appendChild(editButton);

    var deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.setAttribute("data-id", employee.id);
    deleteButton.setAttribute("data-name", employee.name);
    deleteButton.addEventListener("click", function () {
      var id = this.getAttribute("data-id");
      var name = this.getAttribute("data-name");
      var ok = window.confirm("Delete " + name + "?");
      if (!ok) {
        return;
      }
      apiFetch(apiUrl("/api/employees/" + id), { method: "DELETE" })
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          });
        })
        .then(function (result) {
          if (!result.ok) {
            setStatus(readError(result.data, "Could not delete."), "error");
            return;
          }
          setStatus("Employee deleted.", "ok");
          loadEmployees();
        })
        .catch(function () {
          setStatus("Could not delete. Is the API reachable?", "error");
        });
    });
    actionCell.appendChild(deleteButton);

    row.appendChild(actionCell);
    rows.appendChild(row);
    i = i + 1;
  }
}

function loadEmployees(query) {
  var url = apiUrl("/api/employees");
  if (query && query !== "") {
    url = url + "?q=" + encodeURIComponent(query);
  }

  apiFetch(url)
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Could not load employees");
      }
      return response.json();
    })
    .then(function (data) {
      showEmployees(data.employees);
    })
    .catch(function () {
      setStatus("Could not load employees. Is the API reachable?", "error");
    });
}

document.getElementById("search-form").addEventListener("submit", function (event) {
  event.preventDefault();
  var query = document.getElementById("search-query").value.trim();
  loadEmployees(query);
});

document.getElementById("show-all").addEventListener("click", function () {
  document.getElementById("search-query").value = "";
  loadEmployees();
});

document.getElementById("add-form").addEventListener("submit", function (event) {
  event.preventDefault();
  var body = {
    name: document.getElementById("add-name").value,
    department: document.getElementById("add-department").value,
    job_title: document.getElementById("add-job-title").value,
    email: document.getElementById("add-email").value,
  };

  apiFetch(apiUrl("/api/employees"), {
    method: "POST",
    body: JSON.stringify(body),
  })
    .then(function (response) {
      return response.json().then(function (data) {
        return { ok: response.ok, data: data };
      });
    })
    .then(function (result) {
      if (!result.ok) {
        setStatus(readError(result.data, "Could not add employee."), "error");
        return;
      }
      document.getElementById("add-form").reset();
      setStatus("Employee added.", "ok");
      loadEmployees();
    })
    .catch(function () {
      setStatus("Could not add employee. Is the API reachable?", "error");
    });
});

document.getElementById("rate-form").addEventListener("submit", function (event) {
  event.preventDefault();
  var employeeId = document.getElementById("rate-id").value.trim();
  var scoreText = document.getElementById("rate-score").value;
  var comment = document.getElementById("rate-comment").value;
  var body = {
    score: Number(scoreText),
    comment: comment,
  };

  apiFetch(apiUrl("/api/employees/" + employeeId + "/ratings"), {
    method: "POST",
    body: JSON.stringify(body),
  })
    .then(function (response) {
      return response.json().then(function (data) {
        return { ok: response.ok, data: data };
      });
    })
    .then(function (result) {
      if (!result.ok) {
        setStatus(readError(result.data, "Could not save rating."), "error");
        return;
      }
      document.getElementById("rate-form").reset();
      setStatus("Rating saved.", "ok");
      loadEmployees();
    })
    .catch(function () {
      setStatus("Could not save rating. Is the API reachable?", "error");
    });
});

document.getElementById("edit-form").addEventListener("submit", function (event) {
  event.preventDefault();
  var employeeId = document.getElementById("edit-id").value.trim();
  var body = {
    name: document.getElementById("edit-name").value,
    department: document.getElementById("edit-department").value,
    job_title: document.getElementById("edit-job-title").value,
    email: document.getElementById("edit-email").value,
  };

  apiFetch(apiUrl("/api/employees/" + employeeId), {
    method: "PUT",
    body: JSON.stringify(body),
  })
    .then(function (response) {
      return response.json().then(function (data) {
        return { ok: response.ok, data: data };
      });
    })
    .then(function (result) {
      if (!result.ok) {
        setStatus(readError(result.data, "Could not update employee."), "error");
        return;
      }
      document.getElementById("edit-form").reset();
      setStatus("Employee updated.", "ok");
      loadEmployees();
    })
    .catch(function () {
      setStatus("Could not update employee. Is the API reachable?", "error");
    });
});

document.getElementById("signup-form").addEventListener("submit", function (event) {
  event.preventDefault();
  var email = document.getElementById("signup-email").value.trim();
  var password = document.getElementById("signup-password").value;
  cognitoSignUp(email, password)
    .then(function (result) {
      if (!result.ok) {
        setStatus(cognitoMessage(result.data, "Could not sign up."), "error");
        return;
      }
      document.getElementById("confirm-email").value = email;
      setStatus("Check your email for a confirmation code.", "ok");
    })
    .catch(function () {
      setStatus("Could not reach Cognito.", "error");
    });
});

document.getElementById("confirm-form").addEventListener("submit", function (event) {
  event.preventDefault();
  var email = document.getElementById("confirm-email").value.trim();
  var code = document.getElementById("confirm-code").value.trim();
  cognitoConfirm(email, code)
    .then(function (result) {
      if (!result.ok) {
        setStatus(cognitoMessage(result.data, "Could not confirm."), "error");
        return;
      }
      document.getElementById("login-email").value = email;
      setStatus("Email confirmed. You can log in now.", "ok");
    })
    .catch(function () {
      setStatus("Could not reach Cognito.", "error");
    });
});

document.getElementById("login-form").addEventListener("submit", function (event) {
  event.preventDefault();
  var email = document.getElementById("login-email").value.trim();
  var password = document.getElementById("login-password").value;
  cognitoLogin(email, password)
    .then(function (result) {
      if (!result.ok) {
        setStatus(cognitoMessage(result.data, "Could not log in."), "error");
        return;
      }
      refreshAuthView();
      setStatus("Logged in.", "ok");
      loadEmployees();
    })
    .catch(function () {
      setStatus("Could not reach Cognito.", "error");
    });
});

document.getElementById("logout-button").addEventListener("click", function () {
  setIdToken("");
  refreshAuthView();
  setStatus("Logged out.", "ok");
});

refreshAuthView();
if (!cognitoIsOn() || getIdToken()) {
  loadEmployees();
}
