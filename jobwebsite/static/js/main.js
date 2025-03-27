window.addEventListener('scroll', function () {
    const scrollTopButton = document.querySelector('.scroll-top');
    if (window.scrollY > 200) { // Show button after scrolling 200px
        scrollTopButton.style.display = 'block';
    } else {
        scrollTopButton.style.display = 'none';
    }
});
