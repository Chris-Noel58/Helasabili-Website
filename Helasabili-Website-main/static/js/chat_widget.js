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
    input.focus();
  }
  function closeWidget(){
    widget.classList.add('ai-chat-closed');
    panel.setAttribute('aria-hidden','true');
  }

  toggle.addEventListener('click', openWidget);
  closeBtn.addEventListener('click', closeWidget);

  suggestions.addEventListener('click', function(e){
    if(e.target.tagName === 'BUTTON'){
      const q = e.target.dataset.suggestion;
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
          card.style.display = 'flex';
          card.style.gap = '8px';
          card.style.alignItems = 'center';
          card.style.padding = '8px';
          card.style.borderRadius = '8px';
          card.style.border = '1px solid #e6eef3';
          card.style.marginTop = '8px';
          card.style.textDecoration = 'none';
          card.style.color = 'inherit';

          if(item.image){
            const img = document.createElement('img');
            img.src = item.image;
            img.style.width = '72px';
            img.style.height = '54px';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '6px';
            card.appendChild(img);
          }

          const meta = document.createElement('div');
          meta.style.flex = '1';

          const t = document.createElement('div');
          t.textContent = item.title;
          t.style.fontWeight = '600';
          meta.appendChild(t);

          const loc = document.createElement('div');
          loc.textContent = item.location || '';
          loc.style.fontSize = '13px';
          loc.style.color = '#6b7280';
          meta.appendChild(loc);

          if(item.fees){
            const p = document.createElement('div');
            p.textContent = 'KES ' + item.fees;
            p.style.marginTop = '6px';
            p.style.fontWeight = '700';
            p.style.color = '#1f6f3a';
            meta.appendChild(p);
          }

          card.appendChild(meta);

          // actions
          const actions = document.createElement('div');
          actions.style.display = 'flex';
          actions.style.flexDirection = 'column';
          actions.style.gap = '6px';

          const viewBtn = document.createElement('a');
          viewBtn.href = item.detail_url || ('/course/' + item.id + '/');
          viewBtn.textContent = 'View';
          viewBtn.style.background = '#eef6fb';
          viewBtn.style.padding = '6px 8px';
          viewBtn.style.borderRadius = '6px';
          viewBtn.style.textDecoration = 'none';
          viewBtn.style.color = '#0f4a85';

          const bookBtn = document.createElement('a');
          bookBtn.href = item.apply_url || ('/apply/?listing=' + item.id);
          bookBtn.textContent = 'Book';
          bookBtn.style.background = '#2b7a3f';
          bookBtn.style.color = '#fff';
          bookBtn.style.padding = '6px 8px';
          bookBtn.style.borderRadius = '6px';
          bookBtn.style.textDecoration = 'none';

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
