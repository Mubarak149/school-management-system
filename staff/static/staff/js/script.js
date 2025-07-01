
function showSection(section) {
    ['dashboard','classes'].forEach(sec => {
        document.getElementById(sec).style.display = 'none';
    });
    
    document.getElementById(section).style.display = 'block';
}


function showSubjectInput(button) {
    const row = button.closest('tr');
    const subjectCell = row.cells[1];

    // Clear the cell and create subject selection
    subjectCell.innerHTML = `
        <div class="input-group subject-input-group">
            <select class="form-select subject-select">
                <option value="">Select Subject</option>
                <option value="math">Math</option>
                <option value="science">Science</option>
                <option value="history">History</option>
                <!-- Add more subjects as needed -->
            </select>
            <button class="btn btn-primary" onclick="showGradeInput(this)">Next</button>
        </div>
    `;

    // Show the input group
    subjectCell.querySelector('.subject-input-group').style.display = 'flex';
}

function showGradeInput(button) {
    const row = button.closest('tr');
    const subjectCell = row.cells[1];
    const gradeCell = row.cells[2];
    const subjectSelect = subjectCell.querySelector('.subject-select');
    const subject = subjectSelect.value;

    if (!subject) {
        alert('Please select a subject.');
        return;
    }

    // Save the selected subject
    subjectCell.innerHTML = subject.charAt(0).toUpperCase() + subject.slice(1);

    // Clear the grade cell and create grade input group
    gradeCell.innerHTML = `
        <div class="input-group grade-input-group">
            <select class="form-select grade-select">
                <option value="first_test">First Test</option>
                <option value="second_test">Second Test</option>
                <option value="exam">Exam</option>
            </select>
            <input type="number" class="form-control grade-input" placeholder="Grade" min="0" max="100">
            <button class="btn btn-primary" onclick="saveGrade(this)">Save</button>
        </div>
    `;

    // Show the input group
    gradeCell.querySelector('.grade-input-group').style.display = 'flex';
}

function saveGrade(button) {
    const row = button.closest('tr');
    const gradeCell = row.cells[2];
    const gradeInput = gradeCell.querySelector('.grade-input').value;
    const gradeType = gradeCell.querySelector('.grade-select').value;

    if (gradeInput === '' || gradeInput < 0 || gradeInput > 100) {
        alert('Please enter a valid grade between 0 and 100.');
        return;
    }

    // Save the grade (for now, just display it)
    gradeCell.innerHTML = `${gradeType.charAt(0).toUpperCase() + gradeType.slice(1).replace('_', ' ')}: ${gradeInput}`;
}
