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

function showEmployees(employees) {
  var status = document.getElementById("status");
  var table = document.getElementById("employee-table");
  var rows = document.getElementById("employee-rows");

  if (employees.length === 0) {
    status.className = "empty";
    status.textContent = "No employees yet. Add one in the terminal, then refresh.";
    return;
  }

  status.hidden = true;
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

    var ratingCell = document.createElement("td");
    ratingCell.textContent = averageScore(employee.ratings);
    row.appendChild(ratingCell);

    rows.appendChild(row);
    i = i + 1;
  }
}

fetch("/api/employees")
  .then(function (response) {
    if (!response.ok) {
      throw new Error("Could not load employees");
    }
    return response.json();
  })
  .then(showEmployees)
  .catch(function () {
    var status = document.getElementById("status");
    status.className = "error";
    status.textContent = "Could not load employees. Is the server running?";
  });
