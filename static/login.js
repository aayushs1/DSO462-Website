document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const responseMessage = document.getElementById('response-message');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent the form from submitting normally

        const password = document.getElementById('password').value;
        const email = document.getElementById('email').value;

        // Email validation
        const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailPattern.test(email)) {
            alert('Please enter a valid email');
            return;
        }

        // Collect form data
        const formData = new FormData(loginForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        // Send the data to the Flask backend using fetch
        try {
            const response = await fetch('/login-form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            console.log(result)

            // Display success or error message
            if (response.ok) {
                responseMessage.textContent = result.message || "Login successfully!";
                responseMessage.style.color = 'green';
            } else {
                responseMessage.textContent = result.error || "An error occurred.";
                responseMessage.style.color = 'red';
            }
            responseMessage.classList.remove('hidden');
        } catch (error) {
            responseMessage.textContent = "Network error. Please try again later.";
            responseMessage.style.color = 'red';
            responseMessage.classList.remove('hidden');
        }
    });
});