const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
      card.addEventListener('click', () => {
        cards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
      });
    });

    const addBtn = document.getElementById('addBtn');
    const modalOverlay = document.getElementById('modalOverlay');
    const closeBtn = document.getElementById('closeBtn');
    const sendBtn = document.getElementById('sendBtn');

    addBtn.addEventListener('click', () => {
      modalOverlay.style.display = 'flex';
    });
    closeBtn.addEventListener('click', () => {
      modalOverlay.style.display = 'none';
    });
    sendBtn.addEventListener('click', () => {
      const inputVal = document.getElementById('modalInput').value;
      console.log('Gönderildi:', inputVal);
      modalOverlay.style.display = 'none';
    });

    document.addEventListener('DOMContentLoaded', () => {
        const notifications = document.querySelectorAll('.notification');
        notifications.forEach((notification) => {
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 500); 
            }, 3000);
        });
    });