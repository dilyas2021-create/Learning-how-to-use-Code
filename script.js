const form = document.getElementById('contact-form');

function setError(fieldId, message) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(fieldId + '-error');
  field.classList.toggle('invalid', !!message);
  error.textContent = message || '';
}

function validate() {
  let valid = true;

  const name = document.getElementById('name').value.trim();
  if (!name) {
    setError('name', 'Name is required.');
    valid = false;
  } else {
    setError('name', '');
  }

  const email = document.getElementById('email').value.trim();
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) {
    setError('email', 'Email is required.');
    valid = false;
  } else if (!emailPattern.test(email)) {
    setError('email', 'Please enter a valid email address.');
    valid = false;
  } else {
    setError('email', '');
  }

  const message = document.getElementById('message').value.trim();
  if (!message) {
    setError('message', 'Message is required.');
    valid = false;
  } else if (message.length < 10) {
    setError('message', 'Message must be at least 10 characters.');
    valid = false;
  } else {
    setError('message', '');
  }

  return valid;
}

form.addEventListener('submit', function (e) {
  e.preventDefault();

  if (!validate()) return;

  const btn = form.querySelector('button[type="submit"]');
  btn.textContent = 'Sending…';
  btn.disabled = true;

  // Simulate async send (replace with a real endpoint when ready)
  setTimeout(() => {
    form.reset();
    ['name', 'email', 'message'].forEach(id => setError(id, ''));
    btn.textContent = 'Send Message';
    btn.disabled = false;
    document.getElementById('form-success').style.display = 'block';
  }, 1000);
});

// Hide success message when user starts typing again
form.addEventListener('input', function () {
  document.getElementById('form-success').style.display = 'none';
});
