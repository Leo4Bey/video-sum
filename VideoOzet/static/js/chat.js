const chatList = document.getElementById('chatList');
  const chatHeader = document.getElementById('chatHeader');
  const messages = document.getElementById('messages');
  const input = document.getElementById('messageInput');
  const sendBtn = document.getElementById('sendBtn');
  const MAX_HEIGHT = 200; // px

  // Auto-resize textarea
  function adjustHeight() {
    input.style.height = 'auto';
    const newHeight = Math.min(input.scrollHeight, MAX_HEIGHT);
    input.style.height = newHeight + 'px';
  }

  // Initial adjustment
  adjustHeight();

  input.addEventListener('input', () => {
    adjustHeight();
    sendBtn.disabled = input.value.trim() === '';
  });

  // Handle send on Enter, newline on Shift+Enter
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
      input.style.height = 'auto'; // reset height after send
    }
  });

  sendBtn.addEventListener('click', (e) => {
    e.preventDefault();
    sendMessage();
    input.style.height = 'auto';
  });

  function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    // 1. Kullanıcı mesajını ekle
    const userDiv = document.createElement('div');
    userDiv.classList.add('message', 'user');
    const userBubble = document.createElement('div');
    userBubble.classList.add('bubble');
    userBubble.textContent = text;
    userDiv.appendChild(userBubble);
    messages.appendChild(userDiv);
    messages.scrollTop = messages.scrollHeight;

    // 2. Loading animasyonu ekle
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot', 'loading');
    const loadingBubble = document.createElement('div');
    loadingBubble.classList.add('bubble');
    loadingBubble.innerHTML =
      '<span class="dot">·</span>' +
      '<span class="dot">·</span>' +
      '<span class="dot">·</span>';
    loadingDiv.appendChild(loadingBubble);
    messages.appendChild(loadingDiv);
    messages.scrollTop = messages.scrollHeight;

    // Temizle & butonu disable et
    input.value = '';
    sendBtn.disabled = true;

    // 3. Sunucuya POST et
    fetch("", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCSRFToken(),
      },
      body: new URLSearchParams({ "deneme": text }),
    })
    .then(response => {
      if (!response.ok) throw new Error("Sunucu hatası");
      return response.json();
    })
    .then(data => {
      // Loading'i kaldır
      loadingDiv.remove();

      // Bot cevabını ekle
      if (data.bot_reply) {
        const botDiv = document.createElement('div');
        botDiv.classList.add('message', 'bot');
        const botBubble = document.createElement('div');
        botBubble.classList.add('bubble');
        botBubble.textContent = data.bot_reply;
        botDiv.appendChild(botBubble);
        messages.appendChild(botDiv);
        messages.scrollTop = messages.scrollHeight;
      }
    })
    .catch(error => {
      console.error("Gönderim hatası:", error);
      loadingDiv.remove();
      const errDiv = document.createElement('div');
      errDiv.classList.add('message', 'bot');
      const errBubble = document.createElement('div');
      errBubble.classList.add('bubble');
      errBubble.textContent = 'Üzgünüm, bir hata oldu.';
      errDiv.appendChild(errBubble);
      messages.appendChild(errDiv);
      messages.scrollTop = messages.scrollHeight;
    });
  }

  // CSRF token çekme fonksiyonu (cookie'den)
  function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return '';
  }

  // Chat seçimleri
  chatList.addEventListener('click', (e) => {
    if (e.target.tagName === 'LI') {
      document.querySelector('.chat-list li.active')?.classList.remove('active');
      e.target.classList.add('active');
      chatHeader.textContent = e.target.textContent;
      messages.innerHTML = '';
    }
  });