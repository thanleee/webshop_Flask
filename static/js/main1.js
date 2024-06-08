
// tạo scroll menu
let previous = window.pageYOffset;
let screen = window.innerWidth;
function scrolll() {
    window.onscroll = function () {
        let current = window.pageYOffset;
        if (current > previous) {
            document.querySelector("header").classList.add("hidden");
        }
        else {
            document.querySelector("header").classList.remove("hidden");
        }
        previous = current;
    }
}
scrolll();
// tạo menu trái
const bartabb = document.querySelector('#bartab');
bartabb.addEventListener("click", function () {
    const box = document.querySelector('.bartab');
    if (window.getComputedStyle(box).display === 'none') {
        box.style.display = "flex";
        window.onscroll = function () {
            document.querySelector("header").classList.remove("hidden");
        }
    } else {
        slideOut();
    }
});
function slideOut() {
    const box = document.querySelector('.bartab');
    box.style.display = "none";
    scrolll();
}

// ----------login------
function slideOut2() {
    const logIn = document.querySelector('.containerlogin');
    logIn.style.display = "none";
    scrolll();
}
const logInSingUp = document.querySelector('#login-singup');
logInSingUp.addEventListener("click", function () {
    const logIn = document.querySelector('.containerlogin');
    if (window.getComputedStyle(logIn).display === 'none') {
        logIn.style.display = "flex";
        window.onscroll = function () {
            document.querySelector("header").classList.remove("hidden");
        }
    } else {
        slideOut2();
    }
});

function slideOut3() {
    const containcart = document.querySelector('.containcart');
    containcart.style.display = "none";
    scrolll();
}
const viewcart = document.querySelector('#viewcart');
viewcart.addEventListener("click", function () {
    const containcart = document.querySelector('.containcart');
    if (window.getComputedStyle(containcart).display === 'none') {
        containcart.style.display = "flex";
        window.onscroll = function () {
            document.querySelector("header").classList.remove("hidden");
        }
    } else {
        slideOut3();
    }
});



const men = document.querySelector('#men');
const women = document.querySelector('#women');
const menshow = document.querySelector('.menubartab-men');
const womenshow = document.querySelector('.menubartab');

if (window.getComputedStyle(menshow).display === 'flex') {
    women.classList.remove('active');
}
if (window.getComputedStyle(womenshow).display === 'flex') {
    women.classList.add('active');
}
men.addEventListener("click", function () {

    if (window.getComputedStyle(menshow).display === 'none') {
        menshow.style.display = "flex";
        womenshow.style.display = "none";
        men.classList.add('active');
        women.classList.remove('active');
    }
});
women.addEventListener("click", function () {

    if (window.getComputedStyle(womenshow).display === 'none') {
        menshow.style.display = "none";
        womenshow.style.display = "flex";
        women.classList.add('active');
        men.classList.remove('active');
    }
});


//------ section------
const options = document.querySelectorAll('.slidebar-option')
const optionsDisplays = document.querySelectorAll('.option-display')
const girdProduct = document.querySelector('.container')

const changeGrid = (number) => {
    console.log('run')
    if (Number.parseInt(number) === 3) {
        girdProduct.classList.add('gird-3')
        girdProduct.classList.remove('gird-4')
    } else if (Number.parseInt(number) === 4) {
        girdProduct.classList.add('gird-4')
        girdProduct.classList.remove('gird-3')
    }
}

options.forEach((ele, index) => {
    ele.addEventListener('click', () => {
        if (ele.classList.contains('show')) {
            ele.classList.remove('show')
        } else {
            ele.classList.add('show')
        }
    })

})

optionsDisplays.forEach((ele, index) => {
    ele.addEventListener('click', () => {
        if (!ele.classList.contains('active')) {
            ele.classList.add('active')
            if (index === 0) {
                optionsDisplays[1].classList.remove('active')
            } else {
                optionsDisplays[0].classList.remove('active')
            }
            changeGrid(ele.innerText)
        }
    })
})

function toggle() {
    var text = document.getElementById("text");
    var btn = document.getElementById("toggleBtn");
    if (text.style.display === "none") {
        text.style.display = "inline";
        btn.innerHTML = "Read less";
    } else {
        text.style.display = "none";
        btn.innerHTML = "...Read more";
    }
}