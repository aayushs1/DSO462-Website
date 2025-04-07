document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    const responseMessage = document.getElementById('response-message');

    signupForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent the form from submitting normally

        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const email = document.getElementById('email').value;

        // Check if passwords match
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        // Email validation
        const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailPattern.test(email)) {
            alert('Please enter a valid email');
            return;
        }

        // Collect form data
        const formData = new FormData(signupForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        // Send the data to the Flask backend using fetch
        try {
            const response = await fetch('/signup-form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            // Display success or error message
            if (response.ok) {
                responseMessage.textContent = result.message || "Account created successfully!";
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