// Toggle menu on button click
function toggleMobileMenu() {
var menu = document.getElementById('mobile-menu');
if (menu.classList.contains('hidden')) {
    menu.classList.remove('hidden');
    menu.classList.add('block');
} else {
    menu.classList.remove('block');
    menu.classList.add('hidden');
}
}