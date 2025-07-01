
function showSection(section) {
    ['dashboard','studentTableSection',
    'addStudent','teachersViewTableSection','addTeacher'].forEach(sec => {
        document.getElementById(sec).style.display = 'none';
    });
    
    document.getElementById(section).style.display = 'block';
}

// chart logic

// Assuming the top 3 marks for each section are provided as arrays
// For simplicity, we just take the highest mark from each category
const marksData = {
    'Senior Section': [92, 88, 85],
    'Junior Section': [91, 87, 86],
    'Upper Basics': [89, 85, 82],
    'Middle Basics': [93, 90, 88],
    'Lower Basics': [90, 87, 85]
};

const labels = Object.keys(marksData);
const highestMarks = labels.map(label => Math.max(...marksData[label]));

// Bar Chart Data
const barChartData = {
    labels: labels,
    datasets: [{
        label: 'Highest Marks per Section',
        data: highestMarks,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
    }]
};

const barChartConfig = {
    type: 'bar',
    data: barChartData,
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        },
        responsive: true,
        maintainAspectRatio: false
    }
};

// Pie Chart Data - Show counts of top 3 marks for simplicity
const pieChartData = {
    labels: labels,
    datasets: [{
        label: 'Number of Top 3 Marks per Section',
        data: labels.map(label => marksData[label].length),
        backgroundColor: [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)'
        ]
    }]
};

const pieChartConfig = {
    type: 'pie',
    data: pieChartData,
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
};

// Create the charts
new Chart(document.getElementById('barChart'), barChartConfig);
new Chart(document.getElementById('pieChart'), pieChartConfig);


// chart logic end

// students table logic start

document.addEventListener('DOMContentLoaded', function () {
    const students = [
        { avatar: "https://i.pravatar.cc/150?img=1", firstname: "John", lastname: "Smith", regNumber: "001", class: "10A", dateStart: "2022-01-10" },
        { avatar: "https://i.pravatar.cc/150?img=2", firstname: "Jane", lastname: "Doe", regNumber: "002", class: "10B", dateStart: "2022-01-11" },
        { avatar: "https://i.pravatar.cc/150?img=3", firstname: "Alice", lastname: "Johnson", regNumber: "003", class: "10C", dateStart: "2022-01-12" },
        { avatar: "https://i.pravatar.cc/150?img=4", firstname: "Michael", lastname: "Brown", regNumber: "004", class: "11A", dateStart: "2022-01-13" },
        { avatar: "https://i.pravatar.cc/150?img=5", firstname: "Chloe", lastname: "Davis", regNumber: "005", class: "11B", dateStart: "2022-01-14" },
        { avatar: "https://i.pravatar.cc/150?img=6", firstname: "William", lastname: "Wilson", regNumber: "006", class: "11C", dateStart: "2022-01-15" },
        { avatar: "https://i.pravatar.cc/150?img=7", firstname: "Emma", lastname: "Martinez", regNumber: "007", class: "12A", dateStart: "2022-01-16" },
        { avatar: "https://i.pravatar.cc/150?img=8", firstname: "Oliver", lastname: "Garcia", regNumber: "008", class: "12B", dateStart: "2022-01-17" },
        { avatar: "https://i.pravatar.cc/150?img=9", firstname: "Isabella", lastname: "Rodriguez", regNumber: "009", class: "12C", dateStart: "2022-01-18" },
        { avatar: "https://i.pravatar.cc/150?img=10", firstname: "Ethan", lastname: "Martinez", regNumber: "010", class: "10A", dateStart: "2022-01-19" }
       
    ];
    

    const studentTable = document.getElementById('studentTable');
    const searchInput = document.getElementById('searchInput');
    const filterSelect = document.getElementById('filterSelect');

    function populateTable(data) {
        studentTable.innerHTML = data.map(student => `
       
            <tr>
                <td><img src="${student.avatar}" class="avatar" alt="avatar">
                <span class="status-dot online" ></span>
                </td>
                <td>${student.firstname}</td>
                <td>${student.lastname}</td>
                <td>${student.regNumber}</td>
                <td>${student.class}</td>
                <td>${student.dateStart}</td>
                <td><button class = "btn btn-primary btn-sm">
                <a href="http://127.0.0.1:5502/index.html#!" class="nav-link text-light">
                View profile
                </a>
                </button></td>

                <td><button class = "btn btn-dark btn-sm">
                <a href="edit.html#!" class="nav-link text-light">
                Edit profile
                </a>
                </button></td>
            </tr>
           
        `).join('');
    }

    function filterTable() {
        const searchText = searchInput.value.toLowerCase();
        const filterBy = filterSelect.value;
        const filteredStudents = students.filter(student => {
            return (
                (!filterBy || student[filterBy].toLowerCase().includes(searchText)) &&
                (student.firstname.toLowerCase().includes(searchText) || 
                student.lastname.toLowerCase().includes(searchText) || 
                student.regNumber.toLowerCase().includes(searchText) ||
                student.class.toLowerCase().includes(searchText) ||
                student.dateStart.toLowerCase().includes(searchText))
            );
        });
        populateTable(filteredStudents);
    }

    searchInput.addEventListener('input', filterTable);
    filterSelect.addEventListener('change', filterTable);

    populateTable(students); // Initial population of the table
});
// students table logic end

// Teachers table logic start

document.addEventListener('DOMContentLoaded', function () {
    const teachers = [
        { avatar: "https://i.pravatar.cc/150?img=1", firstname: "John", lastname: "Smith", classTeaching: "SS3", subject: "Mathematics/Physics", teachersDateStart: "2022-01-10" },
        { avatar: "https://i.pravatar.cc/150?img=2", firstname: "Jane", lastname: "Doe", classTeaching: "SS2", subject: "English labguage", teachersDateStart: "2022-01-11" },
        { avatar: "https://i.pravatar.cc/150?img=3", firstname: "Alice", lastname: "Johnson", classTeaching: "SS1", subject: "social studies", teachersDateStart: "2022-01-12" },
        { avatar: "https://i.pravatar.cc/150?img=4", firstname: "Michael", lastname: "Brown", classTeaching: "JSS3", subject: "health education", teachersDateStart: "2022-01-13" },
        { avatar: "https://i.pravatar.cc/150?img=5", firstname: "Chloe", lastname: "Davis", classTeaching: "JSS2", subject: "maths", teachersDateStart: "2022-01-14" },
        { avatar: "https://i.pravatar.cc/150?img=6", firstname: "William", lastname: "Wilson", classTeaching: "SS3", subject: "further maths", teachersDateStart: "2022-01-15" },
        { avatar: "https://i.pravatar.cc/150?img=7", firstname: "Emma", lastname: "Martinez", classTeaching: "SS2", subject: "chemistry", teachersDateStart: "2022-01-16" },
        { avatar: "https://i.pravatar.cc/150?img=8", firstname: "Oliver", lastname: "Garcia", classTeaching: "SS1", subject: "biology", teachersDateStart: "2022-01-17" },
        { avatar: "https://i.pravatar.cc/150?img=9", firstname: "Isabella", lastname: "Rodriguez", classTeaching: "JSS1", subject: "Animal husbandary", teachersDateStart: "2022-01-18" },
        { avatar: "https://i.pravatar.cc/150?img=10", firstname: "Ethan", lastname: "Martinez", classTeaching: "SS3", subject: "computer studies", teachersDateStart: "2022-01-19" }
       
    ];

    

    const teachersTable = document.getElementById('teachersTable');
    const searchTeachersInput = document.getElementById('searchTeachersInput');
    const filterTeachersSelect = document.getElementById('filterTeachersSelect');


    
    function populateTeachersTable(items) {
        teachersTable.innerHTML = items.map(teacher => `
       
            <tr>
                <td><img src="${teacher.avatar}" class="avatar" alt="avatar">
                <span class="status-dot online" ></span>
                </td>
                <td>${teacher.firstname}</td>
                <td>${teacher.lastname}</td>
                <td>${teacher.classTeaching}</td>
                <td>${teacher.subject}</td>
                <td>${teacher.teachersDateStart}</td>
                <td><button class = "btn btn-primary btn-sm">
                <a href="http://127.0.0.1:5502/index.html#!" class="nav-link text-light">
                View profile
                </a>
                </button></td>

                <td><button class = "btn btn-dark btn-sm">
                <a href="editteacher.html" class="nav-link text-light">
                Edit profile
                </a>
                </button></td>
            </tr>
           
        `).join('');
    }

    
    function filterTeachersTable() {
        const teachersSearchText = searchTeachersInput.value.toLowerCase();
        const teachersFilterBy = filterTeachersSelect.value;
        const filteredTeachers = teachers.filter(teacher => {
            return (
                (!teachersFilterBy || teacher[teachersFilterBy].toLowerCase().includes(teachersSearchText)) &&
                (teacher.firstname.toLowerCase().includes(teachersSearchText) || 
                teacher.lastname.toLowerCase().includes(teachersSearchText) || 
                teacher.classTeaching.toLowerCase().includes(teachersSearchText) ||
                teacher.subject.toLowerCase().includes(teachersSearchText) ||
                teacher.teachersDateStart.toLowerCase().includes(teachersSearchText))
            );
        });
        populateTeachersTable(filteredTeachers);
    }

    searchTeachersInput.addEventListener('input', filterTeachersTable);
    filterTeachersSelect.addEventListener('change', filterTeachersTable);

    populateTeachersTable(teachers); // Initial population of the table

});

//Teachers table logic end