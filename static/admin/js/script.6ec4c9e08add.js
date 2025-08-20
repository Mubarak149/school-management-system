function showSection(section) {
    ['dashboard', 'studentTableSection', 'addStudent', 'createClassFeeSection'].forEach(sec => {
      const secElement = document.getElementById(sec);
      if (secElement) {
        secElement.style.display = 'none';
      }
    });
  
    const selectedSection = document.getElementById(section);
    if (selectedSection) {
      selectedSection.style.display = 'block';
    }
  }