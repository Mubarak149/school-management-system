// newsArray

let newsElement = [
    'latest news: buying form is soon to begin for new students on the school website...',
    'school will be close by 12:00pm because of ramadan',
    'The new session is soon to begin...',
    'The school computer center is on progress...'
]


let currentIndexElement = 0;

function ChangeText(){
    document.getElementById('newsSticker').innerText = newsElement[currentIndexElement];
    currentIndexElement = (currentIndexElement + 1) % newsElement.length;
}

setInterval(ChangeText,5000);


// welcomeSection observer

document.addEventListener('DOMContentLoaded',function(){
    let welcomeSection = document.getElementById('welcomeSection');

    let observer = new IntersectionObserver((entries) =>{
        entries.forEach((entry) =>{
            if(entry.isIntersecting){
                welcomeSection.style.opacity = 1;
            }else{
                welcomeSection.style.opacity = 0;
            }
        })
    },{
        root : null,
        rootMargin : '0px',
        threshold: 0.3
    })

    observer.observe(welcomeSection);
})


// aboutSection observer

document.addEventListener('DOMContentLoaded',function(){
    let aboutSection = document.getElementById('aboutSection');

    let observer = new IntersectionObserver((entries) =>{
        entries.forEach((entry) =>{
            if(entry.isIntersecting){
                aboutSection.style.opacity = 1;
            }else{
                aboutSection.style.opacity = 0;
            }
        })
    },{
        root : null,
        rootMargin : '0px',
        threshold: 0.2
    })

    observer.observe(aboutSection);
})

// whyChooseUsSection obserer

document.addEventListener('DOMContentLoaded',function(){
    let whyChooseUsSection = document.getElementById('whyChooseUsSection');

    let observer = new IntersectionObserver((entries) =>{
        entries.forEach((entry) =>{
            if(entry.isIntersecting){
                whyChooseUsSection.style.opacity = 1;
            }else{
                whyChooseUsSection.style.opacity = 0;
            }
        })
    },{
        root : null,
        rootMargin : '0px',
        threshold: 0.2
    })

    observer.observe(whyChooseUsSection);
})
// back to top button

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = function() {scrollFunction()};

    function scrollFunction() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            document.getElementById("backToTopBtn").style.display = "block";
        } else {
            document.getElementById("backToTopBtn").style.display = "none";
        }
    }

    // When the user clicks on the button, scroll to the top of the document
    document.getElementById("backToTopBtn").addEventListener("click", function() {
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    });
// administrative  card  functionality
document.addEventListener("DOMContentLoaded", function() {
    let observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
            } else {
                entry.target.classList.remove('in-view');
            }
        });
    }, {
        threshold: 0.5
    });

    document.querySelectorAll('.row').forEach(row => {
        observer.observe(row);
    });
});
// count down 
document.addEventListener('DOMContentLoaded', function () {
    // Set the date we're counting down to
    var countDownDate = new Date("Dec 25, 2024 15:00:00").getTime();

    // Update the countdown every 1 second
    var countdownFunction = setInterval(function () {

        // Get today's date and time
        var now = new Date().getTime();

        // Find the distance between now and the countdown date
        var distance = countDownDate - now;

        // Time calculations for days, hours, minutes, and seconds
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Output the result in an element with id="timer"
        document.getElementById("timer").innerHTML = days + "d " + hours + "h "
        + minutes + "m " + seconds + "s ";

        // If the countdown is over, write some text
        if (distance < 0) {
            clearInterval(countdownFunction);
            document.getElementById("timer").innerHTML = "EVENT STARTED!";
        }
    }, 1000);
});
