function openModal(id) {
    document.getElementById(id).classList.add('open');
    document.body.classList.add('jw-modal-open');
}

function closeModal() {
    document.querySelector('.jw-modal.open').classList.remove('open');
    document.body.classList.remove('jw-modal-open');
}

window.addEventListener('load', function() {
    document.addEventListener('click', event => {
        if (event.target.classList.contains('jw-modal')) {
            closeModal();
        }
    });
});