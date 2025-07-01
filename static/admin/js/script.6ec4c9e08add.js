
function showSection(section) {
    ['dashboard','studentTableSection',
    'addStudent','teachersViewTableSection','addTeacher'].forEach(sec => {
        document.getElementById(sec).style.display = 'none';
    });
    
    document.getElementById(section).style.display = 'block';
}
