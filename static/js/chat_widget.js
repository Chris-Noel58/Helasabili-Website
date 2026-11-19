document.addEventListener('DOMContentLoaded', function(){
  const widget = document.getElementById('ai-chat-widget');
  const toggle = document.getElementById('ai-chat-toggle');
  const panel = document.getElementById('ai-chat-panel');
  const closeBtn = document.getElementById('ai-chat-close');
  const input = document.getElementById('ai-chat-input');
  const send = document.getElementById('ai-chat-send');
  const messages = document.getElementById('ai-chat-messages');
  const suggestions = document.getElementById('ai-chat-suggestions');

  function openWidget(){
    widget.classList.remove('ai-chat-closed');
    panel.setAttribute('aria-hidden','false');
    toggle.setAttribute('aria-expanded','true');
    input.focus();
  }
  function closeWidget(){
    widget.classList.add('ai-chat-closed');
    panel.setAttribute('aria-hidden','true');
    toggle.setAttribute('aria-expanded','false');
    toggle.focus();
  }

  toggle.addEventListener('click', function(){
    if(widget.classList.contains('ai-chat-closed')) openWidget(); else closeWidget();
  });
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && !widget.classList.contains('ai-chat-closed')) closeWidget();
  });
  closeBtn.addEventListener('click', closeWidget);

  suggestions.addEventListener('click', function(e){
    const btn = e.target.closest('button');
    if(btn){
      const q = btn.dataset.suggestion;
      input.value = q;
      sendMessage(q);
    }
  });

  // Render suggestions returned by API
  function renderSuggestions(list){
    if(!Array.isArray(list)) return;
    suggestions.innerHTML = '';
    list.forEach(function(s){
      const btn = document.createElement('button');
      btn.dataset.suggestion = s;
      btn.textContent = s;
      suggestions.appendChild(btn);
    });
  }

  send.addEventListener('click', function(){
    const text = input.value.trim();
    if(!text) return;
    sendMessage(text);
  });

  input.addEventListener('keypress', function(e){
    if(e.key === 'Enter'){
      e.preventDefault();
      send.click();
    }
  });

  function appendBubble(text, cls='ai'){
    const b = document.createElement('div');
    b.className = 'ai-chat-bubble ' + (cls === 'user' ? 'user' : 'ai');
    b.textContent = text;
    messages.appendChild(b);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendMessage(text){
    appendBubble(text, 'user');
    input.value = '';

    // optimistic placeholder
    const placeholder = document.createElement('div');
    placeholder.className = 'ai-chat-bubble ai';
    placeholder.textContent = 'Thinking...';
    messages.appendChild(placeholder);
    messages.scrollTop = messages.scrollHeight;

    try{
      const resp = await fetch('/api/landai/chat/', {
        method: 'POST',
        headers: {'Content-Type':'application/json','X-CSRFToken': getCSRFToken()},
        body: JSON.stringify({message:text})
      });
      const data = await resp.json();
      placeholder.textContent = data.reply || 'Sorry, no reply.';

      // Render any suggestion buttons returned by the API (overrides static suggestions)
      if(Array.isArray(data.suggestions) && data.suggestions.length){
        renderSuggestions(data.suggestions);
      }

      // If listings are returned, render them below the reply
      if(Array.isArray(data.listings) && data.listings.length){
        const container = document.createElement('div');
        container.className = 'ai-listings-container';
        data.listings.forEach(function(item){
          const card = document.createElement('div');
          card.className = 'ai-listing-card';

          if(item.image){
            const img = document.createElement('img');
            img.src = item.image;
            img.alt = '';
            img.loading = 'lazy';
            card.appendChild(img);
          }

          const meta = document.createElement('div');
          meta.className = 'ai-listing-meta';
          const t = document.createElement('strong');
          t.textContent = item.title;
          meta.appendChild(t);
          if(item.location){
            const loc = document.createElement('span');
            loc.textContent = item.location;
            meta.appendChild(loc);
          }
          if(item.fees){
            const p = document.createElement('span');
            p.className = 'ai-listing-price';
            p.textContent = 'KES ' + Number(item.fees).toLocaleString('en-KE');
            meta.appendChild(p);
          }
          card.appendChild(meta);

          const actions = document.createElement('div');
          actions.className = 'actions';
          const viewBtn = document.createElement('a');
          viewBtn.href = item.detail_url || ('/listings/' + item.id + '/');
          viewBtn.textContent = 'View';
          const bookBtn = document.createElement('a');
          bookBtn.href = item.apply_url || ('/apply/?listing=' + item.id);
          bookBtn.textContent = 'Book';
          bookBtn.className = 'is-primary';
          actions.appendChild(viewBtn);
          actions.appendChild(bookBtn);
          card.appendChild(actions);

          container.appendChild(card);
        });
        messages.appendChild(container);
        messages.scrollTop = messages.scrollHeight;
      }
    }catch(err){
      placeholder.textContent = 'Sorry, something went wrong.';
    }
    messages.scrollTop = messages.scrollHeight;
  }

  function getCSRFToken(){
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for(const c of cookies){
      const [k,v] = c.trim().split('=');
      if(k === name) return decodeURIComponent(v);
    }
    return '';
  }
});
